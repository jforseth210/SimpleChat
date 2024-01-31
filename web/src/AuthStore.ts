export function setLoggedIn(isLoggedIn: boolean, username: string){
localStorage.setItem('loggedIn', isLoggedIn.toString());
localStorage.setItem('username', username);
}
export function isLoggedIn(){
  let loggedIn = localStorage.getItem('loggedIn');
  return loggedIn === 'true';
}
export function getUsername(){
  return localStorage.getItem('username');
}
