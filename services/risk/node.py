# from langgraph.types import interrupt 
# from services.loop.state import LoopState 
# from services.risk.engine import RiskEngine  


# class RiskNode:

#     def __init__(
#         self,
#         risk_engine: RiskEngine
#     ): 
#         self.risk_engine = risk_engine

#     def check(self, state: LoopState):
#         last_message = state['messages'][-1]
#         tool_calls = getattr(
#             last_message,
#             "tool_calls",
#             []
#         )
        
#         decisions_list = []  
#         requires_confirmation = False
        
#         for tool_call in tool_calls: 
#             tool_name = tool_call['name']
#             single_decision = self.risk_engine.check(
#                 tool_name
#             )
            
#             decisions_list.append({
#                 "tool_name": tool_name,
#                 "args": tool_call.get("args", {}),
#                 "action": single_decision.action,
#                 "risk_level": single_decision.risk_level.value,
#                 "reason": single_decision.reason
#             })
            
#             if single_decision.action == "reject":
#                 return {
#                     "risk_action": "reject",
#                     "risk_decisions": decisions_list,
#                     "answer": (
#                         f"Tool '{tool_name}' was rejected by risk policy."
#                     )
#                 }

#             if single_decision.action == "confirm":
#                 requires_confirmation = True
                
#         if not requires_confirmation:
#             return {
#                 "risk_action": "allow",
#                 "risk_decisions": decisions_list
#             }

#         approval = interrupt({
#             "type": "tool_confirmation",
#             "message": (
#                 "The requested action requires confirmation."
#             ),
#             "tools": decisions_list
#         })

#         if approval:
#             return {
#                 "risk_action": "allow",
#                 "risk_decisions": decisions_list
#             }
            
#         return {
#             "risk_action": "reject",
#             "risk_decisions": decisions_list,
#             "answer": (
#                 "The requested action was cancelled."
#             )
#         }

from typing import TYPE_CHECKING
from langgraph.types import interrupt 
from services.risk.engine import RiskEngine  

# 1. نضع الاستيراد داخل هذا الشرط ليتجاهله بايثون أثناء التشغيل
if TYPE_CHECKING:
    from services.loop.state import LoopState 

class RiskNode:

    def __init__(
        self,
        risk_engine: RiskEngine
    ): 
        self.risk_engine = risk_engine

    # 2. نضع LoopState بين علامتي تنصيص ليتعامل معها كنص وليس كمتغير فعلي
    def check(self, state: 'LoopState'):
        last_message = state['messages'][-1]
        tool_calls = getattr(
            last_message,
            "tool_calls",
            []
        )
        
        decisions_list = []  
        requires_confirmation = False
        
        for tool_call in tool_calls: 
            tool_name = tool_call['name']
            single_decision = self.risk_engine.check(
                tool_name
            )
            
            decisions_list.append({
                "tool_name": tool_name,
                "args": tool_call.get("args", {}),
                "action": single_decision.action,
                "risk_level": single_decision.risk_level.value,
                "reason": single_decision.reason
            })
            
            if single_decision.action == "reject":
                return {
                    "risk_action": "reject",
                    "risk_decisions": decisions_list,
                    "answer": (
                        f"Tool '{tool_name}' was rejected by risk policy."
                    )
                }

            if single_decision.action == "confirm":
                requires_confirmation = True
                
        if not requires_confirmation:
            return {
                "risk_action": "allow",
                "risk_decisions": decisions_list
            }

        approval = interrupt({
            "type": "confirmation",
            "message": (
                "The requested action requires confirmation."
            ),
            "tools": decisions_list
        })

        if approval:
            return {
                "risk_action": "allow",
                "risk_decisions": decisions_list
            }
            
        return {
            "risk_action": "reject",
            "risk_decisions": decisions_list,
            "answer": (
                "The requested action was cancelled."
            )
        }