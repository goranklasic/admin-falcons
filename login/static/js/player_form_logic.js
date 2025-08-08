
document.addEventListener('DOMContentLoaded', function () {
    // Gender dropdown logic
    const genderSelect = document.getElementById('id_gender_id');
    const genderSpecify = document.getElementById('id_gender_specify').closest('.form-group');

    function toggleGenderSpecify() {
        const val = parseInt(genderSelect.value);
        if ([0, 1, 2].includes(val)) {
            genderSpecify.style.display = 'none';
        } else {
            genderSpecify.style.display = 'block';
        }
    }

    if (genderSelect && genderSpecify) {
        toggleGenderSpecify();
        genderSelect.addEventListener('change', toggleGenderSpecify);
    }

    // Team dropdown logic
    const teamSelect = document.getElementById('id_player_team_id');
    const teamNameInput = document.getElementById('id_player_team');
    const membershipInput = document.getElementById('id_player_membership_amount');

    if (teamSelect && teamNameInput && membershipInput) {
        teamSelect.addEventListener('change', function () {
            const selectedOption = teamSelect.options[teamSelect.selectedIndex];
            const teamName = selectedOption.text;
            const membership = selectedOption.getAttribute('data-membership');
            teamNameInput.value = teamName;
            if (parseFloat(membershipInput.value) === 0 && membership) {
                membershipInput.value = membership;
            }
        });
    }

    // Role dropdown logic
    const roleSelect = document.getElementById('id_player_role_id');
    const roleNameInput = document.getElementById('id_player_role');

    if (roleSelect && roleNameInput) {
        roleSelect.addEventListener('change', function () {
            const selectedOption = roleSelect.options[roleSelect.selectedIndex];
            const roleName = selectedOption.text;
            roleNameInput.value = roleName;
        });
    }
});
