const express = require('express')
const mongoose = require('mongoose')
const path = require('path')
const port = 3333


const app = express()
app.use(express.static(__dirname));
app.use(express.urlencoded({extended:true}))

//Connects to our mongoDB database, will state connection success in the console
//For security, use your own username and password to the database here, ask me for it if you need to- RR
mongoose.connect("mongodb+srv://<usernamehere>:<passwordhere>@secluster.q8vik.mongodb.net/")
const db = mongoose.connection
db.once('open',()=>{
    console.log("Mongodb connection: successful")
})

// The schema showing the two key-value pairs to be stored
const noteSchema = new mongoose.Schema({
    docname:String,
    myTextarea:String
})

// The constructor for sending data based on the above schema
const Notes = mongoose.model('Notes',noteSchema)

app.get('/',(req,res)=>{
    res.sendFile(path.join(__dirname,"TrialPage.html"))
})

//Sends the data from the page to the database onse 'submit' is pressed
app.post('/submit',async (req,res)=>{
    const {docname, myTextarea} = req.body
    const notes = new Notes ({
        docname,
        myTextarea
    })
    await notes.save()
console.log(notes)
res.send("Notes saved to database")
})



app.listen(port,()=>{
    console.log("Server started")
})
