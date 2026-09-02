from abc import ABC, abstractmethod
from decimal import Decimal

from typing import override, Self

from .constantes import UM, ZERO

class Juros(ABC):
    # @property
    # def unidade_tempo(self):
    #     return self._unidade_tempo
    
    def taxa(self, *, base_100=False, indice=False):
        return (self._taxa + (UM if indice else ZERO)) * (100 if base_100 else 1)

    @abstractmethod
    def dividir_unidade_tempo(
        self,
        *,
        razao: int,
        # nova_unidade_tempo: str
    ) -> Self:
        return NotImplemented

    @abstractmethod
    def multiplicar_unidade_tempo(
        self,
        *,
        fator: int,
        # nova_unidade_tempo: str
    ) -> Self:
        return NotImplemented

    def __init__(
        self,
        *,
        taxa: Decimal | str,
        # unidade_tempo = 'DU'
    ):
        # self._unidade_tempo = unidade_tempo
        if type(taxa) == str:
            tratado = taxa.strip()
            if not tratado.endswith('%'):
                raise ValueError('Valores em texto devem informar o símbolo percentual no final. Ex: 12%, 0.5%, 1.005%')
            self._taxa = Decimal(tratado[:-1].rstrip())/100
        elif type(taxa) == Decimal:
            self._taxa = taxa
        else:
            self._taxa = ZERO

    _taxa: Decimal
    # _unidade_tempo: str

    def __str__(self) -> str:
        return f'{self.__class__.__name__}({self.taxa(base_100=True).quantize(Decimal('1.0000'))}%)'

    def __repr__(self) -> str:
        return self.__str__()


class JurosSimples(Juros):
    def __init__(
        self,
        *,
        taxa: Decimal | str,
        # unidade_tempo='DU'
    ):
        super().__init__(
            taxa=taxa,
            # unidade_tempo=unidade_tempo
        )

    @override
    def dividir_unidade_tempo(
        self,
        *,
        razao: int,
        # nova_unidade_tempo: str
    ):
        return JurosSimples(
            taxa=self._taxa / razao,
            # unidade_tempo=nova_unidade_tempo
        )

    @override
    def multiplicar_unidade_tempo(
        self,
        *,
        fator: int,
        # nova_unidade_tempo: str
    ):
        return JurosSimples(
            taxa=self._taxa * fator,
            # unidade_tempo=nova_unidade_tempo
        )


class JurosCompostos(Juros):
    def __init__(self, *, taxa: Decimal | str, unidade_tempo='DU'):
        super().__init__(
            taxa=taxa,
            # unidade_tempo=unidade_tempo
        )

    @override
    def dividir_unidade_tempo(
        self,
        *,
        razao: int,
        # nova_unidade_tempo: str
    ):
        return JurosCompostos(
            taxa=(self.taxa(indice=True) ** (UM/razao)) - UM,
            # unidade_tempo=nova_unidade_tempo
        )

    @override
    def multiplicar_unidade_tempo(
        self,
        *,
        fator: int,
        # nova_unidade_tempo: str
    ):
        return JurosCompostos(
            taxa=(self.taxa(indice=True) ** fator) - UM,
            # unidade_tempo=nova_unidade_tempo
        )