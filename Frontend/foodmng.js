const url = "http://localhost:8000/api/v1/food";

function getFood() {
    let str = ``;
    fetch(url).
        then(response => response.json())
        .then(data => {
            var food = data.data.food;
            for (let i = 0; i < food.length; i++) {
                let item = food[i];
                str += `
                <tr>
                    <th scope="row">${item.FoodId}</th>
                    <td>${item.FoodName}</td>
                    <td><img src="${item.FoodImgUrl}" width="50px;"></td>
                    <td>${item.FoodPrice}</td>
                    <td>${item.FoodAvailability}</td>
                    <td>${item.FoodCategory}</td>
                    <td>
                        <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#exampleModal" onclick="edit('${item.FoodId}', '${item.FoodName}', '${item.FoodPrice}', '${item.FoodAvailability}', )">Edit</button>
                        <button class="btn btn-primary" onclick="del('${item.FoodId}')">Delete</button>
                        <button class="btn btn-primary" onclick="cancelall('${item.FoodId}')">Cancel ${item.FoodName} orders</button>
                    </td>
                </tr>`;
            }
            document.getElementById("food").innerHTML = str;
        })
}

document.getElementById("save_btn").addEventListener("click", function () {
    var formData = new FormData();
    let id = document.getElementById("id").innerText;
    let name = document.getElementById("food_name").value;
    let file = document.getElementById("food_image");
    if ('files' in file) {
        if (file.files.length != 0) {
            formData.append('FoodImg', file.files[0]);
        }
    }
    let price = document.getElementById("food_price").value;
    let avail = "Available";
    let category = document.getElementById("category").value;
    console.log(category);
    if (document.querySelector('input[name="available"]:checked').value == "unavailable") {
        avail = "Unavailable";
    }
    if (name != document.getElementById("fname").innerText) {
        formData.append("FoodName", name);
    }
    formData.append("FoodPrice", price);
    formData.append("FoodAvailability", avail);
    //formData.append("FoodCategory", category);
    let newurl = url + '/' + id;
    fetch(newurl, {
        method: 'PUT',
        body: formData
    })
        .then(response => response.json())
        .then(result => {
            alert("Success:", result);
            location.reload();
        })
        .catch(error => {
            alert('Error:', error);
        });
})

function edit(Id, name, price, availability) {
    document.getElementById("id").innerText = Id;
    document.getElementById("fname").innerText = name;
    document.getElementById("food_name").value = name;
    document.getElementById("food_price").value = price;
    if (availability == 'Available') {
        document.getElementById("available").checked = true;
    }
    else {
        document.getElementById("unavailable").checked = true;
    }
}

function new_food() {
    var formData = new FormData();
    let name = document.getElementById("new_name").value;
    let file = document.getElementById("new_image");
    if ('files' in file) {
        if (file.files.length != 0) {
            formData.append('FoodImg', file.files[0])
            console.log(file.files[0]);
        }
    }
    let price = document.getElementById("new_price").value;
    let avail = "Available";
    let category = document.getElementById("new_category").value;
    formData.append("FoodName", name);
    formData.append("FoodPrice", price);
    formData.append("FoodAvailability", avail);
    formData.append("FoodCategory", category);
    fetch(url, {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(result => {
            alert("Success:", result);
            location.reload();
        })
        .catch(error => {
            alert('Error:', error);
        });
}

function del(id) {
    let newurl = url + '/' + id
    fetch(newurl, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(result => {
        alert("Success:", result);
        location.reload();
    })
    .catch(error => {
        alert('Error:', error);
    });
}

function change() {
    window.location.href = "order.html";
}