import google.generativeai as genai

genai.configure(api_key="")

model = genai.GenerativeModel("gemini-2.5-flash")

print(model.generate_content("hello").text)