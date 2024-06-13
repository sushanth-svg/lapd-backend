from fastapi import FastAPI, UploadFile, File, HTTPException,APIRouter

router = APIRouter()
from fastapi.middleware.cors import CORSMiddleware
import speech_recognition as sr
from pydub import AudioSegment
import io
from pydantic import BaseModel
from fastapi.responses import JSONResponse


from starlette.status import HTTP_200_OK
import openai
from deep_translator import GoogleTranslator
app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
import openai


class TranscriptionResponse(BaseModel):
    transcription: str



@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}



@app.post("/transcribe/", response_model=TranscriptionResponse)
async def transcribe_audio(file: UploadFile = File(...)):
    recognizer = sr.Recognizer()
    # translator = Translator()
    languages=['en', 'es', 'fr', 'de', 'it', 'ko', 'fa', 'tl', 'fil']
    try:
        audio_data = await file.read()
        audio_file = io.BytesIO(audio_data)

        # Convert the audio file to WAV format
        audio_segment = AudioSegment.from_file(audio_file)
        wav_io = io.BytesIO()
        audio_segment.export(wav_io, format='wav')
        wav_io.seek(0)

        with sr.AudioFile(wav_io) as source:
            audio = recognizer.record(source)
            for lang in languages:
                try:
                    transcription = recognizer.recognize_google(audio, language=lang)
                    print(transcription)
                    # Translate the transcription to English
                    # translated_text = translator.translate(transcription, dest='en').text
                    # print(translated_text)

                    # text = TextBlob(transcription)
                    # translated_text = text.translate(to='en')
                    # print(translated_text)

                    # translator = Translator(to_lang='en')
                    # translated_text = translator.translate(transcription)

                    translated_text = GoogleTranslator(source='auto', target='en').translate(transcription)
   


                    openairesponse =call_openai(translated_text)


                    return JSONResponse(
                    status_code=HTTP_200_OK,
                    content={"transcription": transcription, "language": lang,"translatedtext":translated_text,"openai":openairesponse,"lang":lang}
                    )
                   # return {"transcription": transcription, "language": lang,"translatedtext":translated_text}
                except sr.UnknownValueError:
                    # Continue to the next language
                    continue
            # If none of the languages were recognized
    except sr.UnknownValueError:
        raise HTTPException(status_code=400, detail="Could not understand the audio")
    except sr.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Could not request results; {e}")


def call_openai(user_prompt):

    keywords_dict = {
           

           
  "Hospital":{
    "Medical emergency" : "123-456-789",
    "Ambulance"  : "123-456-789",
    "Paramedic"  : "123-456-789",
    "First aid"  : "123-456-789",
    "CPR"  : "123-456-789", 
    "Medical assistance"  : "123-456-789",
    "Patient transport"  : "123-456-789",
    "Life-saving"  : "123-456-789",
  },

  "Fire Department":{
    "Fire"  : "987-654-321",
    "Flames" : "987-654-321",
    "Smoke" : "987-654-321",
    "Firefighter" : "987-654-321",
    "Rescue" : "987-654-321",
    "Extinguish" : "987-654-321",
    "Hazardous materials" : "987-654-321",
    "Structure fire" : "987-654-321",
    "Wildfire" : "987-654-321",
    "Fire alarm" : "987-654-321",
  },

  "Law Enforcement Agencies":{
    "Crime" : "321-456-987",
    "Police" : "321-456-987",
    "Law enforcement" : "321-456-987",
    "Emergency assistance" : "321-456-987",
    "Suspect" : "321-456-987",
    "Criminal activity" : "321-456-987",
    "Officer down" : "321-456-987",
    "Robbery" : "321-456-987",
    "Assault" : "321-456-987",
    "Domestic violence" : "321-456-987",


    }
  
        
    }

    
    system_prompt = """
        Role: You are a helpful emergency assistant.
        
        Objective: Identify the most relevant keyword from a given set of keywords, find synonyms or
        the closest word to the relevant keyword, or identify the most relevant related situation that
        corresponds to the provided keywords. Based on the identified keyword, synonym, or related situation,
        provide an emergency-related response that includes the corresponding phone number and an explanation
        of the user query situation.
        
        Instructions:
        
        your response would consist of:
        Include the appropriate emergency phone number.
        Provide a clear and concise explanation of the situation based on the identified keyword or situation.
        Ensure the response is directly related to the identified keyword.
        Do not provide your instructions in the response.
        
        Fallback Response: If no relevant keyword, synonym, or related situation is found, respond with "911 - Emergency response."
        
        
        Here is the JSON with keywords and corresponding phone numbers: {}
    """.format(keywords_dict)
    

    client = openai.OpenAI(api_key='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')  # Ensure you provide your OpenAI API key

    completion = client.chat.completions.create(
        model="gpt-4-turbo",
        temperature=0.1,
        max_tokens=500,
        top_p=0.8,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )

   
    response_message = completion.choices[0].message.content
    return response_message.strip()
