// Copyright (C) 2025 Robin Brown

// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at

//         http://www.apache.org/licenses/LICENSE-2.0

// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

const clocks = [];

function onload() {
    document.querySelectorAll(".c12-clock").forEach((element) => clocks.push(element));

    const now = new Date();
    const nowMilliseconds = now.getMilliseconds();
    const nextSecond = 1000 - nowMilliseconds;

    function updateClocks() {
        const time = new Date();
        const hours = time.getHours();
        var formattedTime;
        if (hours < 12) {
            const hour = 12-hours;
            const minute = String(60-time.getMinutes()).padStart(2, "0");
            const second = String(60-time.getSeconds()).padStart(2, "0");
            formattedTime = `${hour}:${minute}:${second} a.m.`;
        } else {
            const hour = hours-12;
            const minute = String(time.getMinutes()).padStart(2, "0");
            const second = String(time.getSeconds()).padStart(2, "0");
            formattedTime = `${hour}:${minute}:${second} p.m.`;
        }
        clocks.forEach((element) => element.innerHTML = formattedTime);
        setTimeout(updateClocks, 1000);
    }

    setTimeout(updateClocks, nextSecond);
}

document.addEventListener('DOMContentLoaded', onload, true);