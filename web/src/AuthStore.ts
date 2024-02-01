/*
 * This file contains functions for storing login state in localStorage. 
 *
 * This CAN be modified by the user, and shouldn't be considered secure, 
 * however it's good enough to see where we should navigate since a 401 
 * error will set the login state right back to false.
 */

/*
 * Set the username and login status in localStorage
 */
export function setLoggedIn(isLoggedIn: boolean, username: string){
localStorage.setItem('loggedIn', isLoggedIn.toString());
localStorage.setItem('username', username);
}


/*
 * Get the login status from localStorage
 */
export function isLoggedIn(){
  let loggedIn = localStorage.getItem('loggedIn');
  return loggedIn === 'true';
}


/*
 * Get the username from localStorage
 */
export function getUsername(){
  return localStorage.getItem('username');
}
