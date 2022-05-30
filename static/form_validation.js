function main() {
  if ( !wheel_tyres() ) {
    return false ;
  }

  if ( !flag_patt() ) {
    return false ;
  }

  if ( !consum_pow() ) {
    return false ;
  }


}

// number of wheel can only be equal to or greater than number of tyres...
function wheel_tyres() {
  var wheels_num = document.forms["buggyForm"]["qty_wheels"].value ;
  var tyre_num = document.forms["buggyForm"]["qty_tyres"].value ;

  if (tyre_num < wheels_num) {
    alert("Number of Tyres can only be equal to or greater than number of wheels.") ;

    document.getElementsByName('qty_tyres')[0].style.borderColor = "red";
    document.getElementsByName('qty_wheels')[0].style.borderColor = "red";

    document.forms["buggyForm"]["qty_tyres"].value = wheels_num ;
    
    return false ;
  }

  return true ;

}

// if plain, then set secondary to default. Otherwise, there MUST be another color
// but since it's a closed input, no input is not possible for user to enter.
// In addition to the above, BOTH colours MUST be different...
function flag_patt() {
  var pattern = document.forms["buggyForm"]["flag_pattern"].value ;

  if ( pattern != "plain" ) {
    var pri_col = document.forms["buggyForm"]["flag_color"].value ;
    var sec_col = document.forms["buggyForm"]["flag_color_secondary"].value ;

    if (pri_col == sec_col) {
      alert("Both primary and secondary flag colour cannot be the same.") ;

      document.getElementsByName('flag_color')[0].style.borderColor = "red";
      document.getElementsByName('flag_color_secondary')[0].style.borderColor = "red";
      
      return false
    } ;
  } ;

  return true ;
}

// Can only have one (1) unit if consumable,
// counts for both main power and aux power type.
function consum_pow() {
  const non_consums = ["fusion", "thermo", "solar", "wind"] ;

  var power_type = document.forms["buggyForm"]["power_type"].value ;
  var power_type_num = document.forms["buggyForm"]["power_units"].value ;

  var aux_power_type = document.forms["buggyForm"]["aux_power_type"].value ;
  var aux_power_type_num = document.forms["buggyForm"]["aux_power_units"].value ;

  if (non_consums.includes(power_type) && (power_type_num > 1) ) {
    alert("Non-consumable power motive can only have one (1) unit.") ;

    document.getElementsByName('power_type')[0].style.borderColor = "red" ;
    document.getElementsByName('power_units')[0].style.borderColor = "red" ;

    return false ;
  } ;

  if (non_consums.includes(aux_power_type) && (aux_power_type_num > 1) ) {
    alert("Non-consumable power motive can only have one (1) unit.") ;

    document.getElementsByName('aux_power_type')[0].style.borderColor = "red" ;
    document.getElementsByName('aux_power_units')[0].style.borderColor = "red" ;

    return false ;
  } ;


  return true ;
}