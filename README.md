# ClippyCal
Backend domain-specific language model for ClippyCal: a generative AI-powered voice programming tool enabling creation, updating, deletion, and listing of Google Calendar events through verbal commands, enhancing user accessibility and productivity.

This repository has my contribution of the backend language model of our three-part voice-based system (which consists of a UI frontend, LLM middleend, and language backend). This part is connected to the LLM middleend and takes in translated user input in the format of our programming language. 

To get a better understanding of our research project, reference ClippyCal Backend Poster.pdf.

To understand how to write code in our language, reference specification.txt.

To test out our language, run Driver.py.

Package Installation Guide:
pip3 install google-api-python-client google-auth-httplib2 google-auth-oauthlib