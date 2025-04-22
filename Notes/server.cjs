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


    if (docname == '') {return }

    const notes = new Notes ({
        docname,
        myTextarea
    })

    const projection = { _id: 0, docname: 0, myTextarea: 1}
    var locate = await Notes.collection.findOne({'docname' : docname}, projection)
    if (locate == null) {
       await notes.save() 
    }
    else {
        await Notes.collection.findOneAndUpdate({docname: docname}, { $set: {myTextarea: myTextarea}},
            {new: true},
            (err, notes) =>{
                if (err) {
                    console.error(err)
                    return;
                }
            }
        )
    }
    
console.log(notes)
//res.send("Notes saved to database")
})

async function loadNotes(notename) {
    const projection = { _id: 0, docname: 0, myTextarea: 1}
    try {
      var doc = await Notes.collection.findOne({'docname' : notename}, projection)
    //var testing = (doc.myTextarea)
    //console.log(testing)
    //console.log(doc)
    return doc 
    } catch (error) {
        console.error('Error fetching data: ', error);
        throw error
    }
    
}



//Loads the document with the name entered by the user into the text editor, where it can be edited.
//Currently working on receiving a doc name as imput from the web page.
//Need to work on handling the user searching for documents that don't exist in the doc later
app.get('/trial:dynamic', async (req,res)=>{
    const { dynamic } = req.params
    const { key } = req.query;

    var testdoc = await loadNotes(key)
    console.log(dynamic,key)
    console.log("Hello")
    
    //const projection = { _id: 0, docname: 0, myTextarea: 1}
    //var textdoc = await Notes.collection.findOne({'docname' : 'Rally'}, projection)
    var testing = (testdoc.myTextarea)
    console.log(testing)
    console.log(testdoc)
    res.status(200).json({info: testing})
})



app.listen(port,()=>{
    console.log("Server started")
})
