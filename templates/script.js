//all requests here should go through items, like with express
const apiUrl = "/items";


//load all items from the database
async function loadItems() {
  
  //get results of calling /items
  const res = await fetch(apiUrl);
  
  //read it in as a json 
  const items = await res.json();

  // get the item on the homepage where the list is supposed to go  
  const list = document.getElementById("item-list");
  // remove the current content in list
  list.innerHTML = ""; 

  //for each item in the result
  items.forEach((item) => {
    // make a list item for it     
    const li = document.createElement("li");
    li.textContent = `${item.name} (Qty: ${item.quantity})`;

    //add a button to every entry with a label
    const delBtn = document.createElement("button");
    delBtn.textContent = "Delete";
    //when clicking, make a /delete request with that particular item id
    delBtn.onclick = async () => {
      //using the route in app.js
      await fetch(`${apiUrl}/${item.id}`, { method: "DELETE" });
      //then call this function again to display
      loadItems();
      };
    
    //add the delete button to the list item        
    li.appendChild(delBtn);
    //add that to the current content
    list.appendChild(li);
  });
}

loadItems();



