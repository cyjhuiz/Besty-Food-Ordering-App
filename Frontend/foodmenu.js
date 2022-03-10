const credit_url = "http://localhost:8000/api/v1/credit/";

function getFood() {
    let url = 'http://localhost:8000/api/v1/food';
    fetch(url).
        then(response => response.json())
        .then(data => {
            var food = data.data.food;
            let foodArr = [];
            let smallArr = [];
            let drinkArr = [];
            for (let i = 0; i < food.length; i++) {
                let item = food[i];
                if (item.FoodCategory == "Korean Bowl") {
                    foodArr.push(item);
                }
                else if(item.FoodCategory == "Small Bites") {
                    smallArr.push(item);
                }
                else {
                    drinkArr.push(item);
                }
            }
            let foodStr = createStr(foodArr);
            let smallStr = createStr(smallArr);
            let drinkStr = createStr(drinkArr);
            document.getElementById("food").innerHTML = foodStr;
            document.getElementById("small").innerHTML = smallStr;
            document.getElementById("drink").innerHTML = drinkStr;
            let username = sessionStorage.username;
            document.getElementById("user").innerText = username;
        });
        let newurl = credit_url + sessionStorage.user;
        fetch(newurl)
        .then(response => response.json())
        .then(data => {
            user = data.data;
            document.getElementById("credit").innerText = user[user.length-1].UserCredits;
        });
}

function createStr(food) {
    let close = false;
    let counter = 1;
    let str = ``;
    for (let i=0; i < food.length; i++) {
        let item = food[i];
        if ((counter % 3) == 1) {
            str += `<div class="row mb-3">`;
            close = false;
        }
        str += `
            <div class="col-4">
                <div class="card my-3" style="width: auto;">
                    <img src="${item.FoodImgUrl}" class="card-img-top img-thumbnail">
                    <div class="card-body">
                        <div class="d-flex justify-content-between">
                            <h5 class="card-title">${item.FoodName}</h5>
                            <h5>$${item.FoodPrice}</h5>
                        </div>
                        <br>
                        <div class="row">
                            <div class="col">
                                <div class="input-group">
                                    <button class="btn btn-outline-secondary"
                                        onclick="changeQty('${item.FoodName}', 'minus')">-</button>
                                    <input type="text" class="form-control" id="${item.FoodName}" value="1" min="1">
                                    <button class="btn btn-outline-secondary"
                                        onclick="changeQty('${item.FoodName}', 'plus')">+</button>
                                </div>
                            </div>
                            <div class="col">
                            `;
        if (item.FoodAvailability == "Unavailable") {
            str += `        <button class="btn btn-primary" disabled>Out of stock</button>
        `;
        }
        else {
            str += `        <button class="btn btn-primary" onclick="addItem('${item.FoodId}','${item.FoodImgUrl}','${item.FoodName}','${item.FoodPrice}')">Add to
        Cart</button>
                `;
        }
        str += `            </div>
                        </div>
                    </div>
                </div>
            </div>
            `;
        if ((counter % 3) == 0) {
            str += `</div>`;
            close = true;
        }
        counter++;
    }
    if(!close) {
        str += `</div`;
    }
    return str;
}

function changeQty(id, sign) {
    let qty = parseInt(document.getElementById(id).value);
    if (sign == 'minus') {
        if (qty > 1) {
            document.getElementById(id).value = qty - 1;
        }
    }
    else {
        document.getElementById(id).value = qty + 1;
    }
}

function addItem(id, img, name, price) {
    let qty = parseInt(document.getElementById(name).value);
    if (qty < 1) {
        alert("Please add a valid quantity");
        return;
    }
    let data = {};
    if (sessionStorage.item) {
        data = JSON.parse(sessionStorage.item);
    }
    if (name in data) {
        data[name][3] += qty;
    }
    else {
        data[name] = [id,img,price,qty];
    }
    sessionStorage.setItem("item", JSON.stringify(data));
}

function goToCart() {
    window.location.href = "cart.html";
}

const wrapper = document.getElementById('nav-tabContent');
const nav = document.getElementsByClassName('nav-link');
const active = document.getElementsByClassName('active');

wrapper.addEventListener('click', changeCartNumber);
document.getElementById("cart").onload = changeCartNumber();

function changeCartNumber() {
    let data = {};
    if (sessionStorage.item) {
        data = JSON.parse(sessionStorage.item);
    }
    let length = Object.keys(data).length;
    if (length > 0) {
        document.getElementById('cart').innerText = length;
    }
}