import asyncio
import Services.translate as translate

async def main():
    text_to_translate = "Hello, world!"  # 假设这是你想翻译的文本
    translated_text, status_code, translate_id = await translate.translate_text_to_Chinese(text_to_translate)

    if translated_text is not None:
        print("Translated text:", translated_text)
        print("Translation ID:", translate_id)
        print("Status code:", status_code)
    else:
        print("Failed to translate text, status code:", status_code)

    
# 使用 asyncio.run 来运行主函数
asyncio.run(main())
