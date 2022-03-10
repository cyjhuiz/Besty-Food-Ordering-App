const url = "http://localhost:8000/api/v1/";
//const url = "http://127.0.0.1:5000/email";

function login() {
    let email = document.getElementById("email").value;
    let pw = document.getElementById("password").value;
    if (email == "admin@betsy.com") {
        if (pw == "admin123") {
            window.location.href = "order.html";
            return;
        }
    }
    let newurl = url + "user/email/" + email;
    fetch(newurl)
        .then(response => response.json())
        .then(data => {
            let user = data.data;
            if (pw == user.UserPassword) {
                sessionStorage.setItem("user", user.UserId);
                sessionStorage.setItem("username", user.UserFirstName);
                window.location.href = "foodmenu.html";
            } else {
                alert("Wrong Password");
            }
        })
        .catch(error => {
            alert("Email is not registered.");
        })
}

function signup() {
    let fname = document.getElementById("fname").value;
    let lname = document.getElementById("lname").value;
    let mobile = document.getElementById("mobile").value;
    let email = document.getElementById("newemail").value;
    let pw = document.getElementById("newpassword").value;
    let data = {};
    data["UserFirstName"] = fname;
    data["UserLastName"] = lname;
    data["UserMobile"] = mobile;
    data["UserEmail"] = email;
    data["UserPassword"] = pw;
    data["UserPin"] = null;
    data["UserTBankId"] = null;
    data["UserAccId"] = null;
    console.log(data);
    console.log(typeof (data));
    let newurl = url + "user";
    fetch(newurl, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
    })
        .then(response => response.json())
        .then(result => {
            document.getElementById("signupSuccess").style.display = "block";
            fetch("http://localhost:8000/api/v1/credit/add", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    "UserId": result.data.UserId,
                    "UserCredits": 0
                })
            })
            console.log("Success:", result);
        })
        .catch(error => {
            console.log('Error:', error);
        });
}