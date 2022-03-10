const pay_url = "http://localhost:8000/api/v1/payment/create-payment-intent";
const credit_url = "http://localhost:8000/api/v1/credit/";
const tb_url = "http://localhost:8000/api/v1/place_order";

function retrieveData() {
    let data = JSON.parse(sessionStorage.item);
    var str = ``;
    let total = 0;
    let id = 1;
    for (let key in data) {
        let price = (data[key][2] * data[key][3]);
        total = total + price;
        let price_id = key + '_price';
        str += `
        <tr>
            <th scope="row">${id}</th>
            <td><img src="${data[key][1]}" width="50px;"></td>
            <td>
                <p>${key}</p>
                <div class="row">
                    <div class="col-1">
                        <button class="btn btn-outline-dark" onclick="changeQty('${key}', '${data[key][2]}','minus')">-</button>
                    </div>
                    <div class="col-2">
                        <input type="number" class="form-control" value="${data[key][3]}" size="1" id="${key}">
                    </div>
                    <div class="col-1">
                        <button class="btn btn-outline-dark" onclick="changeQty('${key}', '${data[key][2]}', 'plus')">+</button>
                    </div>
                    <div class="col-1">
                        <button class="btn btn-outline-primary" onclick="remove('${key}')">Remove</button>
                    <div class="col"></div>
                </div>
            </td>
            <td>$<span id="${price_id}">${price.toFixed(2)}</span></td>
        </tr>`;
        id++;
    }
    str += `
            <tr>
                <th scope="row">Total</th>
                <td></td>
                <td></td>
                <td id="total">$${total.toFixed(2)}</td>
            </tr>`;
    document.getElementById("cart_table").innerHTML = str;
    document.getElementById("user").innerText = sessionStorage.username;
    let newurl = credit_url + sessionStorage.user;
    fetch(newurl)
    .then(response => response.json())
    .then(data => {
        user = data.data;
        document.getElementById("credit").innerText = user[user.length-1].UserCredits;
    });
}

function remove(item) {
    let data = JSON.parse(sessionStorage.item);
    console.log(data);
    for (let key in data) {
        if (key == item) {
            delete data[key];
        }
    }
    sessionStorage.setItem("item", JSON.stringify(data));
    location.reload();
}

function changeQty(id, price, sign) {
    let price_id = id + "_price";
    let data = JSON.parse(sessionStorage.item);
    let qty = parseInt(document.getElementById(id).value);
    if (sign == 'minus') {
        if (qty > 1) {
            document.getElementById(id).value = qty - 1;
            document.getElementById(price_id).innerText = ((qty - 1) * price).toFixed(2);
            data[id][3] -= 1;
            let total = parseFloat(document.getElementById("total").innerText.substring(1));
            document.getElementById("total").innerText = '$' + (total - parseFloat(price)).toFixed(2);
        }
    }
    else {
        document.getElementById(id).value = qty + 1;
        document.getElementById(price_id).innerText = ((qty + 1) * price).toFixed(2);
        data[id][3] += 1;
        let total = parseFloat(document.getElementById("total").innerText.substring(1));
        document.getElementById("total").innerText = '$' + (total + parseFloat(price)).toFixed(2);
    }
    sessionStorage.setItem("item", JSON.stringify(data));
}

function change() {
    window.location.href = "foodmenu.html";
}

function tb_checkout() {
    let sstorage = sessionStorage.item;
    sstorage = JSON.parse(sstorage);
    let data = {};
    data["UserId"] = parseInt(sessionStorage.user);
    data["PaymentType"] = "TBank";
    data["orders"] = [];
    for (let key in sstorage) {
        let temp = {};
        temp["OrderItem"] = key;
        temp["ItemPrice"] = parseFloat(sstorage[key][2]);
        temp["ItemQuantity"] = sstorage[key][3];
        temp["FoodId"] = parseInt(sstorage[key][0]);
        data["orders"].push(temp);
    }
    console.log(data);
    console.log(typeof(data));
    fetch(tb_url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        sessionStorage.removeItem("item");
        console.log(result);
        document.getElementById("tbsuccess").style.display = "block";
        setTimeout(function(){ window.location.replace("foodmenu.html"); }, 3000);
        //alert("Successful payment");
    })
    .catch(error => {
        alert('Error:', error);
    })
    
    // let method = document.querySelector('input[name="transfer"]:checked').value;
    // if (method == "credit") {
    //     window.location.href = "checkout.html";
    // }
}
