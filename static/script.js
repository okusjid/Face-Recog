document.getElementById("scrape-form").addEventListener("submit", async function(event) {
    event.preventDefault(); // Prevent the form from submitting the traditional way

    const query = document.getElementById("query").value;
    const resultDiv = document.getElementById("result");

    try {
        const response = await fetch("http://127.0.0.1:8000/start-task/", {
            method: "POST",
            body: new URLSearchParams({
                "name": query
            })
        });

        const data = await response.json();
        if (response.ok) {
            resultDiv.textContent = data.message;
            resultDiv.style.color = "green";
        } else {
            resultDiv.textContent = `Error: ${data.detail}`;
            resultDiv.style.color = "red";
        }
    } catch (error) {
        resultDiv.textContent = `Request failed: ${error.message}`;
        resultDiv.style.color = "red";
    }
});
