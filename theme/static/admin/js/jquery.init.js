/*global jQuery:false*/
'use strict';
/* Puts the included jQuery into django namespace but allowing "conflict"
   so that jQuery remains in both django.jQuery and $
 */
window.django = {jQuery: jQuery};
