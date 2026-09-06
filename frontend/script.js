
// script.js   → frontend logic/API

    async function askAgent() {

    const product = document.getElementById("product").value;
    const price = document.getElementById("price").value;

    const responseBox = document.getElementById("response");


    if (!product || !price) {

        responseBox.style.display = "block";
        responseBox.innerText = "Please enter product and price.";

        return;
    }


    try {

        const response = await fetch( "http://127.0.0.1:5000/agent",{
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    product: product,
                    price: price
                })
            }
        );


        const data = await response.json();


        responseBox.style.display = "block";

        responseBox.innerText = data.response;


    } catch (error) {

        responseBox.style.display = "block";

        responseBox.innerText =
            "Backend server is not running.";

        console.error(error);
    }
}
