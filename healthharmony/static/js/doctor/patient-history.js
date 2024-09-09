export function get_filtered_illnesses_data(illnessesData, filter) {
    let data = []

    if (filter == 'all') {
        data = illnessesData
    } else {
        for (const illness of illnessesData) {
            if (filter == 'not') {
                if (!illness.diagnosis) {
                    data.push(illness)
                }
            } else if (filter == 'done') {
                if (illness.diagnosis) {
                    data.push(illness)
                }
            }
        }
    }

    return data
}
