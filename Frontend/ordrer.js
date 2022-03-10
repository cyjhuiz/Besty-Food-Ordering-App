const order_url = "http://localhost:8000/api/v1/order";
const cancel_url = "http://localhost:8000/api/v1/cancel_order";

function getOrder() {
    let str = ``;
    fetch(order_url).
        then(response => response.json())
        .then(data => {
            var order = data.data.orders;
            for (let i = 0; i < order.length; i++) {
                let item = order[i];
                str += `
                <tr>
                    <th scope="row">${item.OrderId}</th>
                    <td>${item.OrderItem}</td>
                    <td>${item.ItemPrice}</td>
                    <td>${item.ItemQuantity}</td>
                    <td>${item.OrderDate}</td>
                    <td>${item.UserId}</td>
                    <td>${item.OrderStatus}</td>
                    <td>
                        <button class="btn btn-primary" onclick="cancel('${item.FoodId}','${item.OrderId}', ${item.UserId})">Cancel Order</button>
                    </td>
                </tr>`;
            }
            document.getElementById("order").innerHTML = str;
        })
}

function cancel(foodid, orderid, userid) {
    fetch(cancel_url, {
        method: 'POST',
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ "FoodId": foodid, "OrderId": orderid, "UserId": userid })
    })
        .then(response => {
            response.json()
            console.log(response);
        })
        .then(result => {
            alert("Success:", result);
            location.reload();
        })
        .catch(error => {
            alert('Error:', error);
        });
}

function cancelall(id) {
    var newurl = cancel_url + "/FoodAvailability";
    fetch (newurl, {
        method: 'POST',
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ "FoodId": id})
    })
    .then(response => {
        response.json()
        console.log(response);
    })
    .then(result => {
        alert("Success:", result);
        location.reload();
    })
    .catch(error => {
        alert('Error:', error);
    });
}

function change() {
    window.location.href = "foodmng.html";
}