import {Scanner } from 'scanner.js';

document.addEventListener('DOMContentLoaded', function() {
    // Your code here
    let medBtn = document.querySelector('.btn-med-rec');

    medBtn.addEventListener('click', medBtnEvent);
});
function medBtnEvent(){
    console.log('Hi')
}