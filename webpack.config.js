const path = require('path');

module.exports = {
    entry: {
        doctor_overview: './healthharmony/static/js/doctor/overview.js',
        doctor_patient: './healthharmony/static/js/doctor/patient.js',
        doctor_handled: './healthharmony/static/js/doctor/handled.js',
        staff_account: './healthharmony/static/js/staff/account.js',
        staff_inventory: './healthharmony/static/js/staff/inventory.js',
        staff_overview: './healthharmony/static/js/staff/overview.js',
        staff_records: './healthharmony/static/js/staff/records.js',
        patient_overview: './healthharmony/static/js/patient/overview.js',
        patient_profile: './healthharmony/static/js/patient/profile.js',
        patient_record: './healthharmony/static/js/patient/record.js',
        admin_records: './healthharmony/static/js/administrator/records.js',
        admin_account: './healthharmony/static/js/administrator/account.js',
        main: './healthharmony/static/js/general/main.js',
    },
    output: {
        path: path.resolve(__dirname, './healthharmony/static/js/dist')
    }
};
