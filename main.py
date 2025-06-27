from fastapi import FastAPI, UploadFile, File, HTTPException,APIRouter,Form

router = APIRouter()
from fastapi.middleware.cors import CORSMiddleware
import speech_recognition as sr
from pydub import AudioSegment
import io
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from langdetect import detect, DetectorFactory

from starlette.status import HTTP_200_OK
import openai
import langcodes
import json
from deep_translator import GoogleTranslator
from korean_romanizer.romanizer import Romanizer
app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
from starlette.config import Config
config = Config(".env")
open_ai_key = config("OPEN_AI_KEY", cast=str)


# Set seed for reproducibility
DetectorFactory.seed = 0

class TranscriptionResponse(BaseModel):
    transcription: str


languages = {
    'en': 'en-US',   # English
    'hi': 'hi-IN',   # Hindi
    'te': 'te-IN',   # Telugu
    'mr': 'mr-IN',   # Marathi
}



@app.post("/transcribe/", response_model=TranscriptionResponse)
async def transcribe_audio(file: UploadFile = File(...), chathistory: str = Form(None)):
    recognizer = sr.Recognizer()
    # translator = Translator()
        # languageslang=['en', 'es', 'fr', 'de', 'it', 'ko', 'fa', 'tl', 'fil']

    # languages={
    #     'en-US': 'en', 
    #     'hi-IN': 'hi',   # Hindi
    #     'es-ES': 'es',
    #     'fr-FR': 'fr',
    #     'ko-KR': 'ko', 
    #     'fa-IR': 'fa', 
    #     'fil-PH': 'tl',
    #     }
    
    
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
            
             # Try recognizing speech in a general language setting
            transcription = None
            detected_language = None
            
            # for lang_code in languages.values():
            try:
                    # transcription = recognizer.recognize_google(audio, language=lang_code)
                    transcription = recognizer.recognize_google(audio, language="hi-IN,mr-IN,en-US")
                    
                   
                    detected_language = detect(transcription)  # Detect actual spoken language
                    
                    print(f"Transcription: {transcription}, Detected: {detected_language}")

                    
                    # transcription1 = recognizer.recognize_google(audio, language='auto')
                    # detected_language1 = transcription.split()[0] 
                    
                #     print(transcription)
                #     break  # Exit loop on first successful recognition
                # except sr.UnknownValueError:
                #     continue  # Try next language
            except sr.RequestError as e:
                    raise HTTPException(status_code=500, detail=f"Speech recognition API error: {e}")

                
                
            if not transcription or not detected_language:
                raise HTTPException(status_code=400, detail="Could not recognize speech.")

            print(f"Detected language: {detected_language}")
            print(f"Transcription: {transcription}")

            
            
            # Translate transcription to English for OpenAI processing
            if detected_language != 'en':
                translated_text = GoogleTranslator(source=detected_language, target='en').translate(transcription)
            else:
                translated_text = transcription
            
            
                   
            # Call OpenAI with the detected language and transcribed text
            openai_response = call_openai(translated_text, chathistory)

            
            # Translate OpenAI response back to the detected language if needed
            # if detected_language != 'en':
            converted_text = GoogleTranslator(source='en', target='te').translate(openai_response)
            # else:
            #     converted_text = openai_response
                 
                 
                 
            return JSONResponse(
                status_code=200,
                content={
                    "transcription": transcription,
                    "detectedlanguage": detected_language,
                    "translatedtext": translated_text,
                    "openai": openai_response,
                    "convertedtext": converted_text
                }
            )           
                    # return JSONResponse(
                    # status_code=HTTP_200_OK,
                    # content={"transcription": transcription,
                    #           "translatedtext":translated_text,
                    #           "openai":openairesponse,
                    #         #   "detectedlanguage":detected_language,
                    #         #   "convertedtexts":convertedtext,
                    #           "convertedtext":openairesponse}
                    # )
    
    
    
    except sr.UnknownValueError:
        raise HTTPException(status_code=400, detail="Could not understand the audio")
    except sr.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Could not request results; {e}")



def convertTextToDetectedLanguage(openairesponse,detected_language,lang):

    paragraphs = openairesponse.split('\n\n')
    # Check the number of paragraphs
    number_of_paragraphs = len(paragraphs)

    translated_text = GoogleTranslator(source='auto', target='en').translate(openairesponse)

    return translated_text


    

def call_openai(user_prompt,chathistoryjsonstring):
# Parse the JSON string
    chat_history = json.loads(chathistoryjsonstring)


    # thankyou_response = "I understand your concern. Since this is a non-emergency situation, we will dispatch one of our nonprofit volunteers to assist you. They should arrive within an hour."   
    keywords_dict ={
        "noise_complaints": {
            "Noise complaint": "555-0001",
            "Too loud": "555-0002",
            "Excessive noise": "555-0003",
            "Loud music": "555-0004",
            "Loud party": "555-0005",
            "Noise disturbance": "555-0006",
            "Can't sleep": "555-0007",
            "Disturbing the peace": "555-0008",
            "Noise violation": "555-0009",
            "Constant noise": "555-0010"
        },
        "loitering_department": {
            "Public Presence: 555-0011",
            "Presence Activity: 555-0012",
            "Public Behavior: 555-0013",
            "Behavior Monitoring: 555-0014",
            "Suspicious Activity: 555-0015",
            "Public Conduct: 555-0016",
            "Behavior Observance: 555-0017",
            "Public Monitoring: 555-0018",
            "Engaging in Public Activities: 555-0019",
            "Observing Public Conduct: 555-0020"
        },
        "racing_cars": {
            "Racing cars": "555-0021",
            "Street racing": "555-0022",
            "Illegal racing": "555-0023",
            "Car racing": "555-0024",
            "Drag racing": "555-0025",
            "Speeding cars": "555-0026",
            "High-speed chase": "555-0027",
            "Fast cars": "555-0028",
            "Reckless driving": "555-0029",
            "Vehicle racing": "555-0030"
        },
        "traffic_accidents": {
            "Traffic accidents": "555-0031",
            "Vehicle collision": "555-0032",
            "Car crash": "555-0033",
            "Road accident": "555-0034",
            "Traffic collision": "555-0035",
            "Hit and run": "555-0036",
            "Fender bender": "555-0037",
            "Intersection collision": "555-0038",
            "Vehicle damage": "555-0039",
            "Multiple car accident": "555-0040"
        },
        "domestic_disputes": {
            "Domestic dispute": "555-0041",
            "Family argument": "555-0042",
            "Neighbor dispute": "555-0043",
            "Domestic violence": "555-0044",
            "Spousal abuse": "555-0045",
            "Domestic disturbance": "555-0046",
            "Physical altercation": "555-0047",
            "Verbal argument": "555-0048",
            "Domestic conflict": "555-0049",
            "Dispute resolution": "555-0050"
        },
        "drug_related_issues": {
            "Drug activity": "555-051",
            "Narcotics": "555-0052",
            "Drug trafficking": "555-0053",
            "Illegal drugs": "555-0054",
            "Drug abuse": "555-0055",
            "Drug dealing": "555-0056",
            "Substance abuse": "555-0057",
            "Drug possession": "555-0058",
            "Drug trade": "555-0059",
            "Drug-related crime": "555-0060"
    }
}
         
    system_prompt = """
    Role: "You are a multilingual emergency helpful assistant. Respond in the language of the user’s input."
   
    Objective: First, gather personal information from the user step by step to ensure accurate and efficient assistance. Then, identify the most relevant keyword from a given set of keywords, find synonyms or the closest word to the relevant keyword, or identify the most relevant related situation that corresponds to the provided keywords. Based on the identified keyword, synonym, or related situation, provide an emergency-related response that includes the corresponding phone number and name of the department. After your response, provide a Thank You note related to the incident using the provided template.
   
    Instructions:
   
    1. Start by addressing the user's problem or statement. Ask questions one at a time to gather personal information sequentially.
   
    2. Begin with the user's full name:
    - What is your full name?
   
    3. Then, ask for the user's contact number:
    - What is your contact number?
   
    4. Next, ask for the user's location:
    - What is the location of the emergency? (Exact address or nearest landmark)
   
   
    5. After taking all above information reply with: I understand your concern. Since this is a non-emergency situation, we will dispatch one of our nonprofit volunteers to assist you. They should arrive within an hour.
    
    6. Once all the personal information is collected, frame your response in the following format:
   
    I will provide you with a confirmation number for this call. Please note it down: it's [Generate a random 6 digit number].
    
    7. After providing a confirmation number, frame your response:
    You're welcome. A volunteer will be there to help you within the hour. If your situation changes or if you have any more concerns, feel free to call us back.
    add this in different text box saying, "Have a Good day, help is on the way. Goodbye."      
   
    Fallback Response: If no relevant keyword, synonym, or related situation is found, respond with "I couldn't understand what you meant, we are redirecting your call to the Public Safety Department. Here is a quick dial number to the department: +555-0000."
   
    Here is the JSON with keywords and corresponding phone numbers: {}
    """.format(keywords_dict)
    
    
    # Convert the chat history to the format required by OpenAI API
    messages = [{"role": "system", "content": system_prompt}]
    for entry in chat_history:
        messages.append({"role": "user", "content": entry["transcription"]})
        messages.append({"role": "assistant", "content": entry["openai"]})

    # Add the current user prompt
    messages.append({"role": "user", "content": user_prompt})
    

    
    client = openai.OpenAI(api_key=open_ai_key)  # Ensure you provide your OpenAI API key

    completion = client.chat.completions.create(
        model="gpt-4-turbo",
        temperature=0.1,
        max_tokens=500,
        top_p=0.8,
        messages=messages
        # messages=[
        #     {"role": "system", "content": system_prompt},
        #     {"role": "user", "content": user_prompt}
        # ]
    )

   
    response_message = completion.choices[0].message.content

    
    # print(response_message)
    return response_message.strip()






