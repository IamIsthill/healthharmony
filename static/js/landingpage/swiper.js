var swiper = new Swiper(".mySwiper", {
    slidesPerView: 3,
    spaceBetween: 30,
    slidesPerGroup: 3,
    loop: true,
    loopFillGroupWithBlank: true,
    navigation: {
      nextEl: ".swiper-button-next",
      prevEl: ".swiper-button-prev",
    },
  });

  let popup=document.getElementById("popup");
        
  function openPopup(){
      popup.classList.add("open-popup");
  }
  function closePopup(){
      popup.classList.remove("open-popup");
  }
  document.addEventListener('DOMContentLoaded', ()=>{
    openPopup()
  })