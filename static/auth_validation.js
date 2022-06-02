function main() {
    if ( !same_pass() ) {
      return false ;
    }
}

function same_pass() {
   var pass_1 = document.forms["signupForm"]["pwd"].value ;
   var pass_2 = document.forms["signupForm"]["pwd-check"].value ;

  if (!(pass_1 == pass_2)) {
    alert("Passwords are not the same.") ;

    return false ;
  } 

  return true ;
}