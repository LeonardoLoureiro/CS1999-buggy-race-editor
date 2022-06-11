function main() {
    if ( !same_pass() ) {
      return false ;
    }
}

function same_pass() {
   var pass_1 = document.forms["signupForm"]["password"].value ;
   var pass_2 = document.forms["signupForm"]["confirm"].value ;

  if (!(pass_1 == pass_2)) {
    alert("Passwords are not the same.") ;
    document.getElementsByName('password')[0].style.borderColor = "red";
    document.getElementsByName('confirm')[0].style.borderColor = "red";

    return false ;
  } 

  return true ;
}