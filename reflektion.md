Reflektion KK2 Oraklet

1. Säkerhetsaspekter

Under arbetet med projektet har jag funderat en del på vilka säkerhetsrisker som finns, även om applikationen bara är tänkt att köras lokalt. I projektet finns en .env-fil som inte är incheckad i GitHub eftersom den ligger i .gitignore. Det är viktigt eftersom sådana filer ofta innehåller känslig information, till exempel API-nycklar eller andra hemligheter som inte ska vara publika.

I den nuvarande versionen används SmolLM2 lokalt via transformers.pipeline, vilket innebär att jag inte behöver någon extern API-nyckel. Om jag däremot hade valt att använda exempelvis HuggingFace Inference API hade nyckeln hämtats från miljövariabler istället för att skrivas direkt i koden.

En annan sak jag behövde tänka på var filuppladdningen. Eftersom användaren själv kan ladda upp filer finns det alltid en risk att fel typ av fil skickas in. Därför kontrolleras att filen har ändelsen .csv innan den behandlas. Jag fångar även upp vanliga fel, exempelvis om filen är tom eller om Pandas inte kan läsa innehållet.

Det här är dock bara en grundläggande kontroll. Om applikationen skulle användas av riktiga användare hade jag velat lägga till fler skydd, exempelvis begränsningar för filstorlek, bättre felhantering och tydligare loggning. Jag hade också velat säkerställa att interna fel inte visas direkt för användaren.

Jag upptäckte även att prompt injection är något som behöver tas på allvar när man arbetar med språkmodeller. Eftersom användaren själv skriver frågan till modellen går det att försöka påverka dess beteende genom instruktioner som egentligen inte hör till uppgiften. För att minska den risken försöker PromptBuilder tydligt styra modellen att endast använda information från datasetet. Det är ingen perfekt lösning, men det hjälper modellen att hålla sig till den data som faktiskt finns tillgänglig.
