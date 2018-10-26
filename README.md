# Alex-betting-odds-skill

Simple skill that enables Alexa fetch betting odds for 
any football club in the English Premier League (EPL) in
the next round of fixtures

There are 2 parts to this skill:
1. Interaction model
2. Lambda Function

### Building the interaction model
Follow these 
[instructions](https://github.com/alexa/skill-sample-python-fact/blob/master/instructions/1-voice-user-interface.md)
to build the interaction model


### Prepping Lambda for deployment
i. Change directory 

```$ cd lambda```

ii. Install all dependencies as defined in `py/requirements.txt`
into a directory named `skill_env`

```$ pip install -r py/requirements.txt -t skill_env```

iii. Copy the content of `py` into  `skill_env`
 
```$ cp -r py/* skill_env/```

iv. Zip the content `skill_env`. Do not zip the folder itself,
Zip only its content

The .ZIP file is now ready for deployment.