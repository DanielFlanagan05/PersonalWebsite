let count = 0;

// Handle login button click
$("#loginButton").click(function(event) {
    event.preventDefault(); 
    checkCredentials();
});

function checkCredentials() {
    var email = $("#email").val();
    var password = $("#password").val();
    var data_d = {'email': email, 'password': password};

    // Check if the email and password fields are empty
    if (email === "" || password === "") {
        $("#loginStatus").html("Error creating user. Required fields missing.");
        return;
    }

    // Check if the email address is valid
    if (email.includes("@") == false) {
        $("#loginStatus").html("Error creating user. Invalid email address.");
        return;
    } 

    console.log('data_d', data_d);

    // Send the data to the server
    if (email !== "" && password !== "") {
        jQuery.ajax({
            url: "/processlogin",
            data: data_d,
            type: "POST",
            success:function(returned_data){
                returned_data = JSON.parse(returned_data);
                if(returned_data.success) {
                    window.location.href = "/home";
                } else {
                    count++;
                    $("#loginStatus").html('Authentication Failed: Incorrect Password. Attempts: ' + count);
                }
            },
            error: function() {
                count++;
                $("#loginStatus").html('Error during request. Attempts: ' + count);
            }
        });
    }
}
