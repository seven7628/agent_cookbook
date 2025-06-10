# currency-converter.py
from mcp.server.fastmcp import FastMCP
import requests
from typing import Dict, Literal, Optional
from pydantic import BaseModel
# 创建MCP服务器
mcp = FastMCP("Currency Converter")
# 定义转换方向类型
ConversionDirection = Literal["CNY_to_USD", "USD_to_CNY"]
# 定义请求和响应模型
class CurrencyConversionRequest(BaseModel):
    amount: float    
    direction: ConversionDirection
class CurrencyConversionResponse(BaseModel):
    original_amount: float
    converted_amount: float    
    original_currency: str    
    target_currency: str    
    exchange_rate: float

# 获取最新汇率
def get_exchange_rates() -> Dict[str, float]:
    try:        
        # 使用Exchange Rate API获取最新汇率        
        response = requests.get("https://api.exchangerate-api.com/v4/latest/USD")        
        data = response.json()
        print(data)
                        
        # 获取USD到CNY的汇率       
        usd_to_cny = data["rates"]["CNY"]        
         # 计算CNY到USD的汇率        
        cny_to_usd = 1 / usd_to_cny
        
        return {
            "USD_to_CNY": usd_to_cny,
            "CNY_to_USD": cny_to_usd
        }
    except Exception as e:       
        print(f"Error fetching exchange rates: {e}")        
         # 如果API调用失败，使用备用汇率        
        return {            
            "USD_to_CNY": 7.20,  # 备用汇率            
            "CNY_to_USD": 0.139  # 备用汇率       
        }
# 添加货币转换工具
@mcp.tool()
def convert_currency(amount: float, direction: ConversionDirection) -> CurrencyConversionResponse:    
    """    
    将指定金额在人民币(CNY)和美元(USD)之间相互转换
        
     参数:    
     - amount: 要转换的金额    
     - direction: 转换方向，可以是 'CNY_to_USD' 或 'USD_to_CNY'
             
     返回:    
     - 转换结果信息，包括原始金额、转换后金额、汇率等    
     """    
     # 获取最新汇率    
    rates = get_exchange_rates() 
            
     # 根据转换方向执行转换   
    if direction == "CNY_to_USD":        
        original_currency = "CNY"        
        target_currency = "USD"        
        exchange_rate = rates["CNY_to_USD"]        
        converted_amount = amount * exchange_rate    
    else:  # USD_to_CNY        
        original_currency = "USD"        
        target_currency = "CNY"        
        exchange_rate = rates["USD_to_CNY"]        
        converted_amount = amount * exchange_rate        
          
      # 返回结果    
    return CurrencyConversionResponse(        
        original_amount=amount,        
        converted_amount=round(converted_amount, 2),        
        original_currency=original_currency,        
        target_currency=target_currency,        
        exchange_rate=round(exchange_rate, 4)    
    )
# 启动服务器
if __name__ == "__main__":    
    mcp.run()
