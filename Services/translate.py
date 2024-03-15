import httpx, json
import Services.functions as functions

logger = functions.setup_logging()

# 定义一个异步函数，通过webservice将文本翻译成中文
async def translate_text_to_Chinese(text):
  
    # 获取翻译API的URL
    url = functions.get_translation_api_url()
    # 获取翻译源语言和目标语言
    source_lang = functions.get_source_lang()
    target_lang = functions.get_target_lang()
    # 将翻译的文本和目标语言封装成JSON格式
    payload = functions.build_translation_payload(text, source_lang, target_lang)
    # 设置请求头
    headers = {
      'Content-Type': 'application/json'
    }
    # 异步请求翻译API 
    async with httpx.AsyncClient() as client: # 创建一个httpx异步客户端实例
        try:
            response = await client.post(url, headers=headers, data=payload)
            if response.status_code != 200:
                error_message = f"翻译失败，状态码: {response.status_code}"
                logger.error(error_message)
                logger.error(response.text)
                print(error_message)
                return None, response.status_code, None

            json_data = response.json()
            translated_text = json_data.get('data')
            translate_id = json_data.get('id')

        except httpx.RequestError as e:
            error_message = f"Request error occurred during translation: {e}"
            logger.error(error_message)
            # functions.send_error_message(error_message)
            return None, 500, None
        except json.JSONDecodeError as e:
            error_message = f"JSON decoding error: {e}"
            logger.error(error_message)
            # functions.send_error_message(error_message)
            return None, 500, None
        except Exception as e:
            error_message = f"Unexpected error: {e}"
            logger.error(error_message)
            # functions.send_error_message(error_message)
            return None, 500, None

    return translated_text, 200, translate_id
