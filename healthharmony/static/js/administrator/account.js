    // INITIALIZE
    let accountDataFilter = 'all'
    //=============================================

    // Filter account list based on the access
    const accountFilterBtn = document.querySelectorAll('.account-filter')
    accountFilterBtn.forEach((btn) => {
      btn.addEventListener('click', () => {
        let text = btn.getAttribute('data-filter').toLowerCase()
        accountDataFilter = text
        fetchAccountData()
      })
    })
    //=============================================

    // Async function for getting account data from db
    async function fetchAccountData() {
      try {
        const baseUrl = window.location.origin
        let url = new URL(baseUrl + '/api/administrator/accounts/account-list-data/')
        const params = {
          access: accountDataFilter
        }

        // Append parameters to URL
        Object.keys(params).forEach((key) => url.searchParams.append(key, params[key]))

        const response = await fetch(url)
        if (!response.ok) {
          throw new Error('Network response was not ok ' + response.statusText)
        }
        const data = await response.json()
        createAccountData(data)
      } catch (error) {
        console.error('There has been a problem with your fetch operation:', error)
      }
    }

    //=============================================

    // Function to populate account body
    function createAccountData(data) {
      const accountBody = document.querySelector('.account-body')
      let mainHTML = ''
      if (data.length == 0) {
        mainHTML = '<tr><td colspan="4">No available data</td></tr>'
      } else {


      data.forEach((d) => {
        let access = d.access
        access = access.charAt(0).toUpperCase() + access.slice(1).toLowerCase()
        let html = `
                                                                                                                                                                                                <tr>
                                                                                                                                                                                                    <td>${d.first_name} ${d.last_name}</td>
                                                                                                                                                                                                    <td>${d.email}</td>
                                                                                                                                                                                                    <td>${formatDate(d.date_joined)}</td>
                                                                                                                                                                                                    <td>${access}</td>
                                                                                                                                                                                                </tr>
                                                                                                                                                                                             `
        mainHTML += html
      })
    }
      accountBody.innerHTML = mainHTML
    }
    //=============================================

    // Format date
    function formatDate(dateString) {
      const date = new Date(dateString)

      const options = {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: 'numeric',
        minute: 'numeric',
        hour12: true
      }

      return new Intl.DateTimeFormat('en-US', options).format(date)
    }
    //=============================================

    //add account modal
    const addAccountModal = document.getElementById('add-account-modal')

    const addAccountBtn = document.getElementById('add-account-btn')

    // Get the <span> element that closes the modal
    var span = document.getElementsByClassName('close')[0]

    // When the user clicks on the button, open the modal
    addAccountBtn.onclick = function () {
      addAccountModal.style.display = 'block'
    }

    // When the user clicks on <span> (x), close the modal
    span.onclick = function () {
      addAccountModal.style.display = 'none'
    }

    // When the user clicks anywhere outside of the modal, close it
    window.onclick = function (event) {
      if (event.target == addAccountModal) {
        addAccountModal.style.display = 'none'
      }
    }

    //=============================================
