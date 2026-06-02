# Reflektion KK2 – Oraklet

## 1. Säkerhetsaspekter

I projektet har jag försökt tänka på grundläggande säkerhet. Exempelvis ligger `.env` i `.gitignore` så att känslig information som API-nycklar inte riskerar att hamna på GitHub. I den här versionen används dock en lokal modell, vilket innebär att inga externa nycklar behövs.

Jag har även lagt in enkel validering av uppladdade filer genom att kontrollera att de är CSV-filer och hantera vanliga fel som tomma eller ogiltiga filer. Om projektet skulle användas i produktion hade jag velat lägga till fler skydd, exempelvis filstorleksbegränsningar och bättre loggning.

En annan risk är prompt injection, där användaren försöker påverka modellen att ignorera instruktionerna. För att minska risken byggs prompten så att modellen fokuserar på datasetets innehåll.

## 2. Dataskydd och GDPR

Datasetet lagras endast tillfälligt i minnet och sparas inte permanent. Det minskar risken för att data lagras längre än nödvändigt.

Samtidigt kan uppladdade dataset innehålla personuppgifter, vilket innebär att GDPR behöver beaktas om systemet skulle användas i verkligheten. Då hade det krävts tydligare information till användaren, rutiner för radering av data och bättre åtkomstkontroll.

Eftersom modellen körs lokalt skickas inte informationen vidare till externa AI-tjänster, vilket är positivt ur ett dataskyddsperspektiv.

## 3. AI-risker och ansvar

Under arbetet märkte jag att modellen ibland kunde ge svar som lät rimliga men som inte helt baserades på datasetet. Det visar att språkmodeller kan hallucinera och därför inte bör ses som en källa till absoluta fakta.

Jag märkte också att modellens svar kunde variera beroende på hur frågan formulerades. Därför blev promptens utformning en viktig del av lösningen.

För att få stabilare tester valde jag att använda mockade komponenter istället för att köra den riktiga modellen i varje test.

## 4. Designval

Jag valde att dela upp logiken i tre delar: `PromptBuilder`, `LLMRunner` och `ResponseParser`. Det gjorde koden enklare att förstå, testa och felsöka eftersom varje del har ett tydligt ansvar.

Jag använde även Pydantic-modeller för att tydliggöra vilken data som skickas mellan de olika stegen.

Datasetet lagras i minnet istället för i en databas. Jag tycker det är en rimlig lösning för ett skolprojekt, även om datat försvinner när servern startas om.

Den viktigaste lärdomen från projektet är att AI-modellen bara är en del av systemet. Minst lika viktigt är hur data hanteras, hur prompten byggs upp och hur resultatet presenteras för användaren.
