// Scroll to the active li in the list
const scrollableList = document.getElementsByClassName('sublevelnav')[0];
if (typeof scrollableList !== "undefined") {
  const activeItem = scrollableList.querySelector('.active');

  if (activeItem) {
    activeItem.scrollIntoView({block: 'center'});
  }
}
