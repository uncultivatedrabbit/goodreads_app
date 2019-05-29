// front end password verification
function verifyPassword(form){
  username = form.username.value;
  passwordOne = form.password.value;
  passwordTwo = form.confirmation.value;

  // verify the user inputted a username
  if (!username){
    let alert = document.createElement("div");
    let warningNode = document.createTextNode("Please put in a username");
    alert.appendChild(warningNode);
    let element = document.getElementById("username-verify");
    element.appendChild(alert);
    setTimeout(function() {
      $("#username-verify").fadeOut().empty();
    }, 4000);
    event.preventDefault();
    return false;     
  } 
  //verify user inputs a password
  else if (!passwordOne){
    let alert = document.createElement("div");
    let warningNode = document.createTextNode("Please put in your password");
    alert.appendChild(warningNode);
    let element = document.getElementById("password-verify");
    element.appendChild(alert);
    setTimeout(function() {
      $("#password-verify").fadeOut();
    }, 4000);
    event.preventDefault();
    return false;
  } 
  
  // make sure the user puts in password twice
  else if (!passwordTwo){
    alert = document.createElement("div");
    let warningNode = document.createTextNode("Please enter password again.");
    alert.appendChild(warningNode);
    let element = document.getElementById("pass-verify");
    element.appendChild(alert);
    setTimeout(function() {
      $("#pass-verify").fadeOut();
    }, 4000);
    event.preventDefault();
    return false;
  } 
  
  
  else if (passwordOne != passwordTwo){
    let alert = document.createElement("div");
    let warningNode = document.createTextNode("Passwords must match!");
    alert.appendChild(warningNode);
    let element = document.getElementById("confirm-verify");
    element.appendChild(alert);
    setTimeout(function() {
      $("#confirm-verify").fadeOut();
    }, 4000);
    event.preventDefault();
    return false;
  } else {
    return true;
  }
  
}

setTimeout(fade_out, 5000);

function fade_out() {
  $("#registered").fadeOut().remove();
}