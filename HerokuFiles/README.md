## Heroku Files

A couple of files are needed to get your app deployed on Heroku:

A Procfile is a text file in the root directory of your application, to explicitly declare what command should be executed to start your app. Since we want to run our app as a process without a web interface, we need a 'worker' process to run "python <bot_name>.py".

Note: It's important to name your Procfile with a capital 'P' - Heroku won't recognize it otherwise.

More info on Procfiles: https://devcenter.heroku.com/articles/procfile

Heroku recognizes an app as a Python app by looking for key files. Including a requirements.txt in the root directory is one way for Heroku to recognize your Python app. The requirements.txt file lists the app dependencies together. When an app is deployed, Heroku reads this file and installs the appropriate Python dependencies.

Also including a runtime.txt in the root directory also helps Heroku specify which version of Python your app needs to run.

See: https://devcenter.heroku.com/articles/buildpacks#officially-supported-buildpacks for documentation about what files each language requires for Heroku to recognize the app and build it.
