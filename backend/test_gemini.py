from app.config import settings
from app.gemini import gemini_client


print("\n==============================")
print("GEMINI CONNECTION TEST")
print("==============================")

print(
    "API key loaded:",
    bool(settings.GEMINI_API_KEY)
)

print(
    "Gemini enabled:",
    gemini_client.enabled
)

if not gemini_client.enabled:
    print("\n❌ Gemini client is NOT enabled.")
    print("Check your .env file and API key.")
    raise SystemExit(1)


try:

    response = gemini_client.client.models.generate_content(
        model="gemini-3.5-flash",
        contents="Reply with exactly: Gemini connection successful"
    )

    print("\n✅ Gemini request successful!")

    print("\nGemini response:")
    print(response.text)

except Exception as e:

    print("\n❌ Gemini request failed.")

    print(type(e).__name__)
    print(str(e))