(function(){

  // Open the externel links in new window
  var aEls = document.getElementsByTagName('a'),
    reg = new RegExp('/' + window.location.host + '/');
  for (var i = 0; i < aEls.length; i++) {
    if (!reg.test(aEls[i].href)) {
      aEls[i].setAttribute('target', '_blank');
    }
  }

  // Fixed the thead
  $('.table').thfloat();

  // Vote
  $('.vote').click(function(){
    var _this = this;
    var cid = this.dataset.cid;

    $.get('vote', {
      cid: cid,
      tickets: 1
    }, function(r){ // Result
      if (r.indexOf('succeed') > -1) { // Success
        // Change the tickets on table
        var ticketsEl = document.getElementById('tickets-' + cid),
          tickets = Number(ticketsEl.innerText);
        ticketsEl.innerText = tickets + 1;

        // Change `.tickets-plus`
        var ticketsPlusEl = document.getElementById('tickets-plus-' + cid),
          ticketsPlus = ticketsPlusEl.innerText,
          reg = /\(\+(\d+)\)/;

        if (reg.test(ticketsPlus)) {
          ticketsPlus = Number(ticketsPlus.match(reg)[1]) + 1;
          ticketsPlusEl.innerText = '(+' + ticketsPlus + ')';
        } else {
          ticketsPlusEl.innerText = '(+1)';
        }
      } else { // If faild
        $.noticeAdd({
          text: 'Vote faild, maybe something wrong, please try again later. T^T',
          type: 'error',
          stayTime: 6000
        });
      }
    })
  });

  // Vote+
  $('.vote-plus').click(function(){
    var _this = $(this),
      cid = this.dataset.cid;

    $('#vpw').bPopup({
      transition: 'slideDown',
      onOpen: function() {
        var parentEl = _this.parents('tr').children(),
          avatarEl = $('img', parentEl[1]),
          nameEl = parentEl[2],
          unitEl = parentEl[3],
          ticketsEl = $('#tickets-' + cid, parentEl[4]),
          caseEl = $('a', parentEl[5]);

        // Wrap element
        var wrap = $('#vpw');

        // Avatar
        $('#vpw-avatar', wrap).attr('src', avatarEl.attr('src'));

        // Unit
        $('#vpw-unit', wrap).text(unitEl.innerText);

        // Tickets
        $('#vpw-tickets', wrap).text(ticketsEl.text());
        
        // Case
        $('#vpw-case', wrap).text(caseEl.text());
        $('#vpw-case', wrap).attr('href', caseEl.attr('href'));

        // Name
        $('#vpw-name', wrap).text(nameEl.innerText);

        // Cid
        $('#vpw-cid', wrap).val(cid);
      }
    });
  });

  // Submit the Vote+ request
  $('#vpw-submit').click(function(){
    var tickets = $('#vpw-tickets-add').val(),
      cid = $('#vpw-cid').val(),
      reg = /\d+/;

    // Check the input
    if (!reg.test(tickets) || tickets < 1) {
      return;
    }

    // Clear the value
    $('#vpw-tickets-add').val('');

    // Close the popup
    $('#vpw').bPopup().close();

    // Ajax: send the Vote+ request
    $.get('vote', {
      cid: cid,
      tickets: tickets
    }, function(){
      $.noticeAdd({
        text: 'Your Vote+ request has been request, please check out later. : )',
        type: 'success',
        stayTime: 6000
      });
    });
  });

})();