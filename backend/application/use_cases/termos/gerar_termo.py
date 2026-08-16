from datetime import UTC, date, datetime
from uuid import UUID, uuid4

from backend.application.dtos.termo_gerado_dto import (
    GerarTermoInputDTO,
    GerarTermoResultDTO,
    termo_gerado_to_dto,
)
from backend.application.exceptions import PermissaoNegadaError, RecursoNaoEncontradoError
from backend.domain.authorization.policy import Recurso, usuario_pode
from backend.domain.entities.anexo import Anexo, EntidadeAnexavel, TipoArquivo
from backend.domain.entities.termo_gerado import TermoGerado
from backend.domain.entities.usuario import PapelUsuario
from backend.domain.repositories.anexo_repository import AnexoRepository
from backend.domain.repositories.clinica_repository import ClinicaRepository
from backend.domain.repositories.modelo_termo_repository import ModeloTermoRepository
from backend.domain.repositories.paciente_repository import PacienteRepository
from backend.domain.repositories.termo_gerado_repository import TermoGeradoRepository
from backend.domain.services.gerador_documento_service import GeradorDocumentoInterface
from backend.domain.services.storage_service import StorageServiceInterface


def _mesclar_placeholders(corpo_texto: str, contexto: dict[str, str]) -> str:
    resultado = corpo_texto
    for chave, valor in contexto.items():
        resultado = resultado.replace(f"{{{{{chave}}}}}", valor)
    return resultado


class GerarTermoUseCase:
    def __init__(
        self,
        modelo_termo_repository: ModeloTermoRepository,
        paciente_repository: PacienteRepository,
        clinica_repository: ClinicaRepository,
        termo_gerado_repository: TermoGeradoRepository,
        anexo_repository: AnexoRepository,
        storage_service: StorageServiceInterface,
        gerador_documento: GeradorDocumentoInterface,
    ) -> None:
        self._modelo_termo_repository = modelo_termo_repository
        self._paciente_repository = paciente_repository
        self._clinica_repository = clinica_repository
        self._termo_gerado_repository = termo_gerado_repository
        self._anexo_repository = anexo_repository
        self._storage_service = storage_service
        self._gerador_documento = gerador_documento

    async def executar(
        self,
        paciente_id: UUID,
        dto: GerarTermoInputDTO,
        clinica_id: UUID,
        usuario_id: UUID,
        usuario_nome: str,
        papel: PapelUsuario,
    ) -> GerarTermoResultDTO:
        if not usuario_pode(papel, Recurso.TERMO_GERACAO):
            raise PermissaoNegadaError("Papel sem permissao para gerar termo")

        paciente = await self._paciente_repository.buscar_por_id(paciente_id, clinica_id)
        if paciente is None:
            raise RecursoNaoEncontradoError("Paciente nao encontrado")

        modelo = await self._modelo_termo_repository.buscar_por_id(dto.modelo_id, clinica_id)
        if modelo is None:
            raise RecursoNaoEncontradoError("Modelo de termo nao encontrado")
        if not modelo.ativo:
            raise ValueError("Modelo de termo esta desativado")

        clinica = await self._clinica_repository.buscar_por_id(clinica_id)
        nome_clinica = clinica.nome if clinica is not None else ""

        contexto = {
            "nome_paciente": paciente.nome_completo,
            "data_nascimento": paciente.data_nascimento.isoformat(),
            "idade": str(paciente.idade),
            "nome_mae": paciente.nome_mae,
            "nome_pai": paciente.nome_pai,
            "diagnostico": paciente.diagnostico or "",
            "queixa_principal": paciente.queixa_principal or "",
            "nome_profissional": usuario_nome,
            "nome_clinica": nome_clinica,
            "data_atual": date.today().isoformat(),
        }
        corpo_mesclado = _mesclar_placeholders(modelo.corpo_texto, contexto)
        pdf_bytes = await self._gerador_documento.gerar_pdf(modelo.nome, corpo_mesclado)

        nome_arquivo = f"{modelo.nome}.pdf"
        storage_ref = await self._storage_service.salvar(pdf_bytes, nome_arquivo)

        agora = datetime.now(UTC)
        anexo = Anexo(
            id=uuid4(),
            clinica_id=clinica_id,
            criado_em=agora,
            atualizado_em=agora,
            deletado=False,
            deletado_em=None,
            entidade_tipo=EntidadeAnexavel.PACIENTE,
            entidade_id=paciente_id,
            tipo_arquivo=TipoArquivo.PDF,
            nome_arquivo=nome_arquivo,
            storage_ref=storage_ref,
            criado_por=usuario_id,
        )
        anexo_salvo = await self._anexo_repository.salvar(anexo)

        termo_gerado = TermoGerado(
            id=uuid4(),
            clinica_id=clinica_id,
            criado_em=agora,
            atualizado_em=agora,
            deletado=False,
            deletado_em=None,
            paciente_id=paciente_id,
            modelo_id=modelo.id,
            anexo_id=anexo_salvo.id,
            gerado_por=usuario_id,
        )
        termo_salvo = await self._termo_gerado_repository.salvar(termo_gerado)

        return GerarTermoResultDTO(pdf_bytes=pdf_bytes, termo=termo_gerado_to_dto(termo_salvo))
