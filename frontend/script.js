const API = "https://imagedehazer.onrender.com"

let user_id = null


async function signup(){

let email = document.getElementById("signup_email").value
let password = document.getElementById("signup_pass").value

let res = await fetch(API + "/signup",{
method:"POST",
headers:{
"Content-Type":"application/json"
},
body:JSON.stringify({
email:email,
password:password
})
})

let data = await res.json()

if(data.status==="success"){
alert("Signup successful")
}else{
alert("Signup failed")
}

}


async function login(){

let email=document.getElementById("login_email").value
let password=document.getElementById("login_pass").value

let res=await fetch(API + "/login",{
method:"POST",
headers:{
"Content-Type":"application/json"
},
body:JSON.stringify({
email:email,
password:password
})
})

let data=await res.json()

if(data.status==="success"){

user_id=data.user_id

document.getElementById("auth").style.display="none"
document.getElementById("dashboard").style.display="block"

}else{

alert("Invalid login")

}

}


async function upload(){

let file=document.getElementById("image").files[0]

let form=new FormData()

form.append("user_id",user_id)
form.append("image",file)

let res=await fetch(API + "/dehaze",{
method:"POST",
body:form
})

let blob = await res.blob()

let url = URL.createObjectURL(blob)

let a = document.createElement("a")
a.href = url
a.download = "dehazed.jpg"

document.body.appendChild(a)
a.click()
a.remove()

}


async function loadHistory(){

let res=await fetch(API + "/history/" + user_id)

let data=await res.json()

let html="<h3>History</h3>"

data.forEach(img=>{

html+=`<div class="history-card">
<a href="${API}/download?path=${img}" target="_blank">Download Image</a>
</div>`

})

document.getElementById("history").innerHTML=html

}
