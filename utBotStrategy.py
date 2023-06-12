import octobot_commons.constants as common_constants
import octobot_commons.enums as common_enums
import octobot_evaluators.evaluators as evaluators
import octobot_evaluators.enums as enums

import numpy as np
import tulipy as ti

class utBotStrategyEvaluator(evaluators.StrategyEvaluator):

    def init_user_inputs(self, inputs: dict) -> None:
        """
        Called right before starting the tentacle, should define all the tentacle's user inputs unless
        those are defined somewhere else.
        """
        super().init_user_inputs(inputs)
        self.UI.user_input(common_constants.CONFIG_TENTACLES_REQUIRED_CANDLES_COUNT, common_enums.UserInputTypes.INT,
                        200, inputs, min_val=200,
                        title="Initialization candles count: the number of historical candles to fetch from "
                              "exchanges when OctoBot is starting.")

    def get_full_cycle_evaluator_types(self) -> tuple:
        # returns a tuple as it is faster to create than a list
        return enums.EvaluatorMatrixTypes.TA.value, enums.EvaluatorMatrixTypes.SCRIPTED.value

    async def matrix_callback(self,
                              matrix_id,
                              evaluator_name,
                              evaluator_type,
                              eval_note,
                              eval_note_type,
                              exchange_name,
                              cryptocurrency,
                              symbol,
                              time_frame):
        data = await self.get_exchange_symbol_data(symbol)
        close_data = data[PriceIndexes.IND_PRICE_CLOSE.value]
        atr = ti.atr(np.array(close_data), 10)
        xATR = atr[-1]
        nLoss = 1 * xATR
        src = close_data[-1]
        
        xATRTrailingStop = 0.0
        iff_1 = src > xATRTrailingStop[-1] if src - nLoss else src + nLoss
        iff_2 = src < xATRTrailingStop[-1] and src < xATRTrailingStop[-1] if min(xATRTrailingStop[-1], src + nLoss) else iff_1
        xATRTrailingStop = src > xATRTrailingStop[-1] and src > xATRTrailingStop[-1] if max(xATRTrailingStop[-1], src - nLoss) else iff_2
        
        pos = 0
        iff_3 = src < xATRTrailingStop[-1] and src < xATRTrailingStop[-1] if -1 else pos[-1]
        pos = src < xATRTrailingStop[-1] and src > xATRTrailingStop[-1] if 1 else iff_3
        
        self.eval_note = pos
        await self.strategy_completed(cryptocurrency, symbol, time_frame=time_frame)
