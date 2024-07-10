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
import openai
from starlette.config import Config
config = Config(".env")
open_ai_key = config("OPEN_AI_KEY", cast=str)


# Set seed for reproducibility
DetectorFactory.seed = 0

class TranscriptionResponse(BaseModel):
    transcription: str




@app.post("/transcribe/", response_model=TranscriptionResponse)
async def transcribe_audio(file: UploadFile = File(...), chathistory: str = Form(None)):
    recognizer = sr.Recognizer()
    # translator = Translator()
        # languageslang=['en', 'es', 'fr', 'de', 'it', 'ko', 'fa', 'tl', 'fil']

    languages={
        'en-US': 'en', 
        'es-ES': 'es',
        'fr-FR': 'fr',
        'ko-KR': 'ko', 
        'fa-IR': 'fa', 
        'fil-PH': 'tl',
        }
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
            for locale,lang in languages.items():
                try:
                    transcription = recognizer.recognize_google(audio, language=locale)
                    print(transcription)


                    translated_text = GoogleTranslator(source='auto', target='en').translate(transcription)
                    # Detect the language of the transcription
                    detected_language_code = detect(transcription)
                    detected_language = langcodes.Language.get(detected_language_code).display_name()

                    openairesponse =call_openai(transcription,chathistory)

                    if(openairesponse):

                        convertedtext= convertTextToDetectedLanguage(openairesponse,detected_language,lang)

                    

                    
                    

                    return JSONResponse(
                    status_code=HTTP_200_OK,
                    content={"transcription": transcription,
                              "translatedtext":translated_text,
                              "openai":openairesponse,
                              "detectedlanguage":detected_language,
                              "convertedtext":convertedtext}
                    )
                except sr.UnknownValueError:
                    # Continue to the next language
                    continue
            # If none of the languages were recognized
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


    # if(number_of_paragraphs>1):
    #     translated_text = GoogleTranslator(source='auto', target=lang).translate(paragraphs[1])
    #     if(lang == 'ko'):


    #         # Romanize Korean text to English transliteration
    #         romanized_text = Romanizer(translated_text).romanize()

    #         print(romanized_text)
    #         translated_text=romanized_text


    #     return translated_text
    # else:
    #     return ""    
         
    


def call_openai(user_prompt,chathistoryjsonstring):
# Parse the JSON string
    chat_history = json.loads(chathistoryjsonstring)


    thankyou_response = "Thank you for informing us. We understand and We've logged your complaint and will dispatch an officer. Please call us back if you have further concerns."   
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
           
#     system_prompt = """
#         Role: You are a helpful emergency assistant.

#         Objective: First, gather personal information from the user step by step to ensure accurate and efficient assistance. 
#         Then, identify the most relevant keyword from a given set of keywords, find synonyms or
#         the closest word to the relevant keyword, or identify the most relevant related situation that
#         corresponds to the provided keywords. Based on the identified keyword, synonym, or related situation,
#         provide an emergency-related response that includes the corresponding phone number and name of the department.
#         After your response, provide a Thank You note related to the incident. You can refer to the template for the Thank You note.

#         template: """ + thankyou_response + """
        
#         Instructions:
        
#         . Ask additional questions based on the nature of the emergency to gather detailed information:
   
#    a. **Nature of the Emergency**
#       - What is the nature of your emergency? (e.g., medical emergency, crime in progress, accident, suspicious activity)
#       - Is anyone in immediate danger? (e.g., Are there any injuries? Is there a threat to someone's life?)

#    b. **Location**
#       - What is the location of the emergency? (Exact address or nearest landmark)
#       - Where are you calling from? (If different from the location of the emergency)

#    c. **Time**
#       - When did the incident occur? (Is it happening now? Did it just happen? Has it been a while?)

#    d. **Detailed Information**
#       - Can you describe what happened? (Details of the incident)
#       - What actions have you taken so far? (e.g., Have you tried to leave the area? Have you contacted anyone else?)

#    e. **Suspect Information** (if applicable)
#       - Can you describe the suspect(s)? (Gender, age, race, clothing, distinguishing features)
#       - Do you know the suspect? (Is the suspect known to the victim?)
#       - Are there any weapons involved? (Type of weapon, if any)

#    f. **Vehicle Information** (if applicable)
#       - Can you describe the vehicle? (Make, model, color, license plate number)
#       - Which direction did the vehicle go? (Direction of travel if the suspect fled)

#    g. **Victim Information**
#       - Is anyone injured? (Nature and extent of injuries)
#       - Do you need medical assistance? (Is an ambulance required?)

#    h. **Caller Information**
#       - What is your name?
#       - What is your phone number? (In case the call gets disconnected or further contact is needed)
#       - Are you safe where you are? (Ensuring the caller’s safety)

         
#         Collect each piece of information in sequence before proceeding to the next question.

        



#         Once all the personal information is collected, frame your response in the following format:
        
#         We have redirected your call to [name of the department]. Here is a quick dial number to the department: [corresponding phone number].
        
#         Thank you note.

#         Fallback Response: If no relevant keyword, synonym, or related situation is found, respond with "I couldn't understand what you meant, we are redirecting your call to the Public Safety Department. Here is a quick dial number to the department: +555-0000."
        
#         Here is the JSON with keywords and corresponding phone numbers: {}
#     """.format(keywords_dict)

    system_prompt = """
    Role: You are a helpful emergency assistant.
   
    Objective: First, gather personal information from the user step by step to ensure accurate and efficient assistance. Then, identify the most relevant keyword from a given set of keywords, find synonyms or the closest word to the relevant keyword, or identify the most relevant related situation that corresponds to the provided keywords. Based on the identified keyword, synonym, or related situation, provide an emergency-related response that includes the corresponding phone number and name of the department. After your response, provide a Thank You note related to the incident using the provided template.
   
    Thank You Note Template: """ + thankyou_response + """
   
    Instructions:
   
    1. Start by addressing the user's problem or statement. Ask questions one at a time to gather personal information sequentially.
   
    2. Begin with the user's full name:
    - What is your full name?
   
    3. Next, ask for the user's location:
    - What is the location of the emergency? (Exact address or nearest landmark)
    - Where are you calling from? (If different from the location of the emergency)
   
    4. Then, ask for the user's contact number:
    - What is your contact number?
   
    5. Inquire about the nature of the emergency:
    - What is the nature of your emergency? (e.g., medical emergency, crime in progress, accident, suspicious activity)
    - Is anyone in immediate danger? (e.g., Are there any injuries? Is there a threat to someone's life?)
   
    6. Ask additional questions based on the nature of the emergency to gather detailed information:
   
    a. **Time**
        - When did the incident occur? (Is it happening now? Did it just happen? Has it been a while?)
   
    b. **Detailed Information**
        - Can you describe what happened? (Details of the incident)
        - What actions have you taken so far? (e.g., Have you tried to leave the area? Have you contacted anyone else?)
   
    c. **Suspect Information** (if applicable)
        - Can you describe the suspect(s)? (Gender, age, race, clothing, distinguishing features)
        - Do you know the suspect? (Is the suspect known to the victim?)
        - Are there any weapons involved? (Type of weapon, if any)
   
    d. **Vehicle Information** (if applicable)
        - Can you describe the vehicle? (Make, model, color, license plate number)
        - Which direction did the vehicle go? (Direction of travel if the suspect fled)
   
    e. **Victim Information**
        - Is anyone injured? (Nature and extent of injuries)
        - Do you need medical assistance? (Is an ambulance required?)
   
    f. **Caller Information**
        - Are you safe where you are? (Ensuring the caller’s safety)
   
    7. Once all the personal information is collected, frame your response in the following format:
   
    We have redirected your call to [Please provide a random American Name here] at [name of the department]. Your ticket number is [Please provide a random 2 digit number here].
   
        Thank you note.  
   
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
    

    # Combine the chat history with the new user prompt
    # messages = [{"role": "system", "content": system_prompt}] + chat_history + [{"role": "user", "content": user_prompt}]
    

    # system_prompt = """
    #     Role: You are a helpful emergency assistant.
        
    #     Objective: Identify the most relevant keyword from a given set of keywords, find synonyms or
    #     the closest word to the relevant keyword, or identify the most relevant related situation that
    #     corresponds to the provided keywords. Based on the identified keyword, synonym, or related situation,
    #     provide an emergency-related response that includes the corresponding phone number and name of the department.
    #     After your response provide me a Thank You note related to the incident. you can refer the template for thank you note.

    #     template: """ + thankyou_response + """
        
    #     Instructions:
        
    #     frame your response in the following format:
 
    #     We have Redirected your call to [ name of the department ] Here is a quick dial number to the department: [corresponding phone number] 
        
    #     Thank you note.

    #     Fallback Response: If no relevant keyword, synonym, or related situation is found, respond with "I couldn't understand what you meant, we are redirecting your call to Public Safety Department. Here is a quick dial number to the department:+555-0000."
        
        
    #     Here is the JSON with keywords and corresponding phone numbers: {}
    # """.format(keywords_dict)
    







    # name of the department and corresponding phone number "911 - Emergency response."

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




# def convertLanguageToAudio()





# @app.get("/")
# def read_root():
#     return {"Hello": "World"}

# @app.get("/items/{item_id}")
# def read_item(item_id: int, q: str = None):
#     return {"item_id": item_id, "q": q}



 # Translate the transcription to English
                    # translated_text = translator.translate(transcription, dest='en').text
                    # print(translated_text)

                    # text = TextBlob(transcription)
                    # translated_text = text.translate(to='en')
                    # print(translated_text)

                    # translator = Translator(to_lang='en')
                    # translated_text = translator.translate(transcription)


#                      keywords_dict = {
           

           
#   "Hospital":{
#     "Medical emergency" : "123-456-789",
#     "Ambulance"  : "123-456-789",
#     "Paramedic"  : "123-456-789",
#     "First aid"  : "123-456-789",
#     "CPR"  : "123-456-789", 
#     "Medical assistance"  : "123-456-789",
#     "Patient transport"  : "123-456-789",
#     "Life-saving"  : "123-456-789",
#   },

#   "Fire Department":{
#     "Fire"  : "987-654-321",
#     "Flames" : "987-654-321",
#     "Smoke" : "987-654-321",
#     "Firefighter" : "987-654-321",
#     "Rescue" : "987-654-321",
#     "Extinguish" : "987-654-321",
#     "Hazardous materials" : "987-654-321",
#     "Structure fire" : "987-654-321",
#     "Wildfire" : "987-654-321",
#     "Fire alarm" : "987-654-321",
#   },

#   "Law Enforcement Agencies":{
#     "Crime" : "321-456-987",
#     "Police" : "321-456-987",
#     "Law enforcement" : "321-456-987",
#     "Emergency assistance" : "321-456-987",
#     "Suspect" : "321-456-987",
#     "Criminal activity" : "321-456-987",
#     "Officer down" : "321-456-987",
#     "Robbery" : "321-456-987",
#     "Assault" : "321-456-987",
#     "Domestic violence" : "321-456-987",


#     }
  
        
#     }

    


      
    # system_prompt = """
    #     Role: You are a helpful emergency assistant.
        
    #     Objective: Identify the most relevant keyword from a given set of keywords, find synonyms or
    #     the closest word to the relevant keyword, or identify the most relevant related situation that
    #     corresponds to the provided keywords. Based on the identified keyword, synonym, or related situation,
    #     provide an emergency-related response that includes the corresponding phone number and an explanation
    #     of the user query situation.
        
    #     Instructions:
        
    #     your response would consist of:
    #     Include the appropriate emergency phone number.
    #     Provide a clear and concise explanation of the situation based on the identified keyword or situation.
    #     Ensure the response is directly related to the identified keyword.
    #     Do not provide your instructions in the response.
        
    #     Fallback Response: If no relevant keyword, synonym, or related situation is found, respond with "911 - Emergency response."
        
        
    #     Here is the JSON with keywords and corresponding phone numbers: {}
    # """.format(keywords_dict)
    
