from decimal import Decimal

from .constantes import ZERO

class MovimentacaoCaixa:
    """
    Metadados do fluxo de caixa.
    """

    @property
    def valor(self) -> Decimal:
        """
        Valor financeiro no momento da movimentação.
        """
        return self._valor

    @property
    def tempo(self) -> int:
        """
        Momento em que a movimentação ocorrerá, de acordo com a configuração do fluxo de caixa.

        `tempo == 10` pode significar 10 dias corridos, 10 dias úteis ou 10 de outra unidade temporal. Quem terá essa informação será o fluxo de caixa.
        """
        return self._tempo

    @property
    def rotulo_id(self) -> int | None:
        """
        Identificador do rótulo da movimentação no contexto do fluxo de caixa ao qual pertence.

        Por exemplo, o fluxo de caixa ao qual a movimentação pertence pode ter os seguintes identificadores:
        1. "Aplicação"
        2. "Juros"
        3. "Vencimento"

        Se a movimentação possui `rotulo_id == 2`, significa que ela é um pagamento de juros.
        """
        return self._rotulo_id

    def __init__(
        self,
        *,
        valor: int | float | Decimal,
        tempo: int,
        rotulo_id: int | None = None
    ):
        self._valor = Decimal(valor)
        self._tempo = tempo
        self._rotulo_id = rotulo_id

    def __str__(self) -> str:
        return f'MovimentacaoCaixa(tempo={self.tempo}, rotulo_id={self.rotulo_id}, valor={self.valor})'

    def __repr__(self) -> str:
        return self.__str__()

    _valor: Decimal
    _tempo: int
    _rotulo_id: int | None


class MovimentacoesAgregadas:
    """
    Agrega as movimentações de forma temporal e pré-calcula o valor total.
    """

    @property
    def tempo(self) -> int:
        return self._tempo

    @property
    def movimentacoes(self) -> list[MovimentacaoCaixa]:
        return [*self._movs]

    @property
    def total(self) -> Decimal:
        return self._total

    def __init__(self, tempo: int):
        self._tempo = tempo
        self._movs = []
        self._total = ZERO

    def incluir(self, movimentacao: MovimentacaoCaixa):
        """
        Inclui uma movimentação e recalcula o valor total agregado.
        """
        if movimentacao.tempo != self._tempo:
            raise IndexError(f'Você não pode agregar uma movimentação que está em um tempo diferente do contexto no qual ela está sendo agregada. Tempo da movimentação: {movimentacao.tempo}. Tempo da agregação: {self._tempo}.')
        self._movs.append(movimentacao)
        self._total += movimentacao.valor

    def remover(self, movimentacao: MovimentacaoCaixa):
        """
        Remove a primeira movimentação igual à informada e recalcula o valor total agregado.
        """
        indice = -1
        for i, mov in enumerate(self._movs):
            if (
                mov.tempo == movimentacao.tempo and
                mov.valor == movimentacao.valor and
                mov.rotulo_id == movimentacao.rotulo_id
            ):
                indice = i
                break
        if indice != -1:
            mov = self._movs.pop(indice)
            self._total -= mov.valor

    def __str__(self) -> str:
        return f'MovimentacoesAgregadas(tempo={self.tempo}, movimentacoes={len(self.movimentacoes)}, total={self.total})'

    def __repr__(self) -> str:
        return self.__str__()

    _tempo: int
    _movs: list[MovimentacaoCaixa]
    _total: Decimal


class FluxoCaixa:
    """
    Classe auxiliar para distribuição, controle e agregação das movimentações no eixo temporal.
    """

    @property
    def unidade_tempo(self) -> str:
        """
        Unidade arbitrária de tempo para detalhar a menor unidade de tempo do fluxo de caixa.
        
        Exemplo: `"DC"`, `"Dias úteis"`, `"Mês"`, `"ANO"`
        """
        return self._unidade_tempo

    @property
    def rotulos_movimentacoes(self) -> dict[int, str]:
        """
        Identificador e descrição de cada tipo de movimentação.

        Exemplo: `{ 1: "Aplicação", 2: "Juros", 3: "Vencimento" }`
        """
        return {**self._rotulos_movimentacoes}

    @property
    def movimentacoes(self) -> list[MovimentacaoCaixa]:
        """
        Lista todas as movimentações individualmente.
        """
        todas: list[MovimentacaoCaixa] = []
        for agg in self._movs.values():
            todas += agg.movimentacoes
        return todas

    @property
    def movimentacoes_por_tempo(self) -> dict[int, MovimentacoesAgregadas]:
        """
        Lista todas as unidades de tempo que possuem pelo menos uma movimentação, de forma agregada.
        """
        return {**self._movs}

    def __init__(
        self,
        *,
        movimentacoes: list[MovimentacaoCaixa] = [],
        unidade_tempo: str = 'DU',
        rotulos_movimentacoes: dict[int, str] = {},
    ):
        self._unidade_tempo = unidade_tempo
        self._rotulos_movimentacoes = {**rotulos_movimentacoes}
        self._movs = {}
        for movimentacao in movimentacoes:
            self.incluir(movimentacao)

    def incluir(self, movimentacao: MovimentacaoCaixa):
        """
        Inclui movimentação no fluxo de caixa.
        """
        if (
            movimentacao.rotulo_id != None and
            movimentacao.rotulo_id not in self._rotulos_movimentacoes
        ):
            raise KeyError(f'Movimentações com identificação de rótulo precisam ser criadas em fluxos de caixa com os identificadores definidos. Identificador informado na movimentação: {movimentacao.rotulo_id}. Rótulos do fluxo de caixa: {self.rotulos_movimentacoes}')
        t = movimentacao.tempo
        movs = self._movs[t] if t in self._movs else MovimentacoesAgregadas(movimentacao.tempo)
        movs.incluir(movimentacao)
        self._movs[t] = movs

    def remover(self, movimentacao: MovimentacaoCaixa):
        """
        Remove a primeira movimentação com as características informadas do fluxo de caixa.
        """
        t = movimentacao.tempo
        mov = self._movs.get(t)
        if not mov:
            return
        mov.remover(movimentacao)
        if len(mov.movimentacoes) == 0:
            del self._movs[t]

    def __str__(self) -> str:
        return f'FluxoCaixa(unidades_tempo={len(self.movimentacoes_por_tempo)}, movimentacoes={len(self.movimentacoes)})'

    def __repr__(self) -> str:
        return self.__str__()

    _unidade_tempo: str
    _rotulos_movimentacoes: dict[int, str]
    _movs: dict[int, MovimentacoesAgregadas]