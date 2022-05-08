from app import app

app.config['SECRET_KEY'] = 'password-super-dificil'
app.run(debug=True)
