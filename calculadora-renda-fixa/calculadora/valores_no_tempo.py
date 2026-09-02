from math import e
from typing import Mapping

from .fluxo_caixa import FluxoCaixa, MovimentacaoCaixa
from .juros import Juros, JurosCompostos, JurosSimples
from .constantes import UM

class ValorPresente:
    fluxo_caixa: FluxoCaixa
    """
    Fluxo de caixa esperado no período.
    """

    taxas_juros: dict[int, Juros]
    """
    A partir de qual unidade de tempo determinada taxa de juros começa a valer.
    """

    def __init__(
        self,
        *,
        fluxo_caixa: FluxoCaixa,
        taxas_juros: Juros | Mapping[int, Juros]
    ):
        self.fluxo_caixa = fluxo_caixa
        if type(taxas_juros) == dict:
            if 0 not in taxas_juros:
                raise ValueError('A taxa de juros inicial (tempo 0) precisa ser informada.')
            self.taxas_juros = taxas_juros
        elif isinstance(taxas_juros, Juros):
            self.taxas_juros = { 0: taxas_juros }
        else:
            raise TypeError('Você só pode passar um valor de Juros ou um dicionário de intervalo + ...')

    def calcular(self) -> FluxoCaixa:
        tx_juros = self.taxas_juros
        movs_agg = self.fluxo_caixa.movimentacoes_por_tempo

        t_eventos_alteracao_juros = set(tx_juros.keys())
        t_eventos_fluxo_caixa = set(movs_agg.keys())
        t_eventos = sorted(t_eventos_alteracao_juros | t_eventos_fluxo_caixa)

        fc_vp = FluxoCaixa()

        ultimo_t_juros_acruados = 0
        juros_validos_ate_agora = tx_juros[0]
        juros_acumulados_indice = UM
        for t in t_eventos:
            # Acrua juros entre períodos de eventos
            t_acruando_juros = t - ultimo_t_juros_acruados
            juros = (
                juros_validos_ate_agora
                .multiplicar_unidade_tempo(fator=t_acruando_juros)
            )
            juros_acumulados_indice = (
                juros_acumulados_indice * juros.taxa(indice=True) if isinstance(juros, JurosCompostos) else
                juros_acumulados_indice + juros.taxa() if isinstance(juros, JurosSimples) else
                juros_acumulados_indice # ?
            )
            ultimo_t_juros_acruados = t

            # Atualiza qual taxa de juros usar após a mudança
            alteracao_juros = tx_juros.get(t)
            if alteracao_juros:
                juros_validos_ate_agora = alteracao_juros

            # Calcula valor presente para cada movimentação do fluxo de caixa
            pgto_fluxo_caixa = movs_agg.get(t)
            if pgto_fluxo_caixa:
                for mov in pgto_fluxo_caixa.movimentacoes:
                    valor_presente = mov.valor / juros_acumulados_indice
                    fc_vp.incluir(MovimentacaoCaixa(tempo=t, valor=valor_presente, rotulo_id=mov.rotulo_id))

        return fc_vp