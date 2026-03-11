const API = "https://image1dehazer.onrender.com"

let USER_ID = null


async function signup(){

const email = document.getElementById("signup_email").value
const password = document.getElementById("signup_password").value

const res = await fetch(API + "/signup",{

method:"POST",
headers:{
"Content-Type":"application/json"
},

body:JSON.stringify({
email:email,
password:password
})

})

const data = await res.json()

alert(data.status)

}



async function login(){

const email = document.getElementById("login_email").value
const password = document.getElementById("login_password").value

const res = await fetch(API + "/login",{

method:"POST",
headers:{
"Content-Type":"application/json"
},

body:JSON.stringify({
email:email,
password:password
})

})

const data = await res.json()

if(data.status==="success"){

USER_ID = data.user_id

document.getElementById("auth").style.display="none"
document.getElementById("dashboard").style.display="block"

}else{

alert("Invalid login")

}

}



async function uploadImage(){

const file = document.getElementById("image").files[0]

if(!file){

alert("Please select image")
return

}

const formData = new FormData()

formData.append("image",file)
formData.append("user_id",USER_ID)

const res = await fetch(API + "/dehaze_image",{

method:"POST",
body:formData

})

const blob = await res.blob()

const url = window.URL.createObjectURL(blob)

const a = document.createElement("a")

a.href=url
a.download="dehazed.jpg"

document.body.appendChild(a)
a.click()
a.remove()

}



async function loadHistory(){

const res = await fetch(API + "/history/"+USER_ID)

const images = await res.json()

const div = document.getElementById("history")

div.innerHTML=""

images.forEach(img=>{

const image = document.createElement("img")

image.src = API + "/download?path=" + img

div.appendChild(image)

})

}
