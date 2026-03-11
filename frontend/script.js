let user_id=null

async function signup(){

let email=document.getElementById("signup_email").value
let password=document.getElementById("signup_pass").value

await fetch("/signup",{
method:"POST",
headers:{"Content-Type":"application/json"},
body:JSON.stringify({email,password})
})

alert("Signup successful")

}

async function login(){

let email=document.getElementById("login_email").value
let password=document.getElementById("login_pass").value

let res=await fetch("/login",{
method:"POST",
headers:{"Content-Type":"application/json"},
body:JSON.stringify({email,password})
})

let data=await res.json()

if(data.status==="success"){

user_id=data.user_id

document.getElementById("auth").style.display="none"
document.getElementById("dashboard").style.display="block"

}

}

async function upload(){

let file=document.getElementById("image").files[0]

let form=new FormData()

form.append("user_id",user_id)
form.append("image",file)

let res=await fetch("/dehaze",{
method:"POST",
body:form
})

let blob=await res.blob()

let url=URL.createObjectURL(blob)

let a=document.createElement("a")
a.href=url
a.download="dehazed.jpg"
a.click()

}

async function loadHistory(){

let res=await fetch("/history/"+user_id)

let data=await res.json()

let html="<h3>History</h3>"

data.forEach(img=>{
html+=`<br><a href="/download?path=${img}" target="_blank">Download</a>`
})

document.getElementById("history").innerHTML=html

}
