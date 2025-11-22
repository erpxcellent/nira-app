from nira import create_app

# Create App
app = create_app()

if __name__ == '__main__':
    app.run(port='5020',debug=True)
