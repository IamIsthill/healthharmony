import {
  formatDate,
  openModal,
  closeModal
} from '/static/js/utils.js'

const user_data = JSON.parse(document.getElementById('user_data').textContent)

handle_user_filters()
handle_change_user_access()

// when user change the access
function handle_change_user_access() {
  const select_elements = document.querySelectorAll('.js_change_access')

  for (const select_element of select_elements) {
    select_element.addEventListener('change', (event) => {
      const user_id = select_element.getAttribute('data-user-id')
      const user = get_user_data(user_id)
      const access = select_element.value
      let access_text = ''

      if (access == 1) {
        access_text = 'Patient'
      }

      else if (access == 2) {
        access_text = 'Staff'
      }

      else if (access == 3) {
        access_text = 'Doctor'
      }

      else if (access == 4) {
        access_text = 'Admin'
      }

      // select the form then create the data

      const access_form = document.querySelector('.js_access_form_body')
      access_form.innerHTML = `
        <h4>Change the access level for ${user.email} to ${access_text}? </h4>
        <input type="hidden" name="user_id" value="${user_id}" />
        <input type="hidden" name="access" value="${access}" />
      `

      const access_modal = document.querySelector('.js_access_modal')
      const close_btn = document.querySelectorAll('.js_close_access_form')

      openModal(access_modal)

      for (const close of close_btn) {
        closeModal(access_modal, close)
        close.addEventListener('click', () => {
          // revert back the access to previous
        select_element.value = user.access

        })
      }

    })
  }
}

// When user clicks the filter buttons
function handle_user_filters() {
  const btns = document.querySelectorAll('.js-account-filter')

  for (const btn of btns) {
    btn.addEventListener('click', () => {
      for (const btn of btns) {
        btn.classList.remove('js-account-filter-active')
      }
      btn.classList.add('js-account-filter-active')
      const paginated_user_data = get_filtered_user_data()
      update_account_table(paginated_user_data)
      handle_change_user_access()

    })
  }
}

// Get the active filter
function get_active_account_filter() {
  const btn = document.querySelector('.js-account-filter-active')
  return parseInt(btn.getAttribute('data-filter'))
}

// get the current page
function get_current_account_page() {
  const url = new URL(window.location.href)
  const page = url.searchParams.get('page')
  return page
}

// filter and paginate user data
function get_filtered_user_data() {
  const filter = get_active_account_filter()
  const filtered_user_data = filter_user_data(filter)
  const page = get_current_account_page()
  const paginated_user_data = paginateArray(filtered_user_data, page)
  return paginated_user_data
}

//filter user data
function filter_user_data(filter) {
  let data = []
  if (filter == 0) {
    return user_data
  }
  else {
    for (const user of user_data) {
      if (parseInt(user.access) == parseInt(filter)) {
        data.push(user)
      }
    }
  }
  return data
}

// update the account table
function update_account_table(paginated_user_data) {
  const account_body_element = document.querySelector('.js_account_body')
  account_body_element.innerHTML = ''

  if(paginated_user_data.length == 0) {
    account_body_element.innerHTML = `
    <tr><td colspan="4">No available data</td></tr>
    `
  } else {
    let html = ''

    for (const user of paginated_user_data) {
      html += `
      <tr>
        <td>${ user.first_name ? user.first_name : '' } ${ user.last_name ? user.last_name : ''}</td>
        <td>${ user.email }</td>
        <td>${formatDate(user.date_joined)}</td>
        <td>
          <div>
            <select name="access" class="js_change_access" data-user-id="${user.id}">
                <option value="1" ${ user.access == 1 ? 'selected' : ''}>Patient</option>
                <option value="2" ${ user.access == 2 ? 'selected' : ''}>Staff</option>
                <option value="3" ${ user.access == 3 ? 'selected' : ''}>Doctor</option>
                <option value="4" ${ user.access == 4 ? 'selected' : ''}>Admin</option>
            </select>
          </div>
        </td>
      </tr>
      `
    }
    account_body_element.innerHTML = html
  }

}

function paginateArray(array, page) {
  if (!page) {
      page = 1
  }

  page = parseInt(page)
  let itemStart = page * 20 - 19
  let itemEnd = page * 20
  if (itemStart > array.length) {
      page = Math.ceil(array.length / 20)
      itemStart = page * 20 - 19
      itemEnd = page * 20

  }
  let paginatedArray = []

  for (let key in array) {
      key = parseInt(key)
      if (key + 1 >= itemStart && key + 1 <= itemEnd) {
          paginatedArray.push(array[key])
      }
  }
  return paginatedArray
}

// get the user data based on the id
function get_user_data(id) {
  for(const user of user_data) {
    if (parseInt(user.id) == parseInt(id)) {
      return user
    }
  }
  return null
}
