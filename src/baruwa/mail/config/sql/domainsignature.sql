-- htmlsigs.customize
-- Inline HTML Signature
CREATE OR REPLACE VIEW htmlsigs AS
-- email aliases
SELECT CONCAT("From:\t", user_addresses.address, "\t%signature-dir%/users/html/", auth_user.id, ".html") rule,
'htmlsigs' collate utf8_unicode_ci as name FROM user_addresses, user_signatures, auth_user WHERE
auth_user.is_active = 1 AND user_addresses.enabled = 1 AND auth_user.id = user_addresses.user_id
AND user_addresses.user_id = auth_user.id AND user_signatures.enabled = 1 AND
user_signatures.signature_type = 2 AND user_addresses.address_type = 2 UNION
-- user email
SELECT CONCAT("From:\t", auth_user.email, "\t%signature-dir%/users/html/", auth_user.id, ".html") rule,
'htmlsigs' collate utf8_unicode_ci as name FROM  user_signatures, auth_user, profiles WHERE 
auth_user.is_active = 1 AND auth_user.id = profiles.user_id AND
user_signatures.user_id = auth_user.id AND user_signatures.enabled = 1
AND user_signatures.signature_type = 2 UNION
-- domains
SELECT CONCAT("From:\t", '*@', user_addresses.address, "\t%signature-dir%/domains/html/", user_addresses.id, ".html") rule,
'htmlsigs' name FROM domain_signatures INNER JOIN user_addresses ON domain_signatures.useraddress_id = user_addresses.id
WHERE domain_signatures.enabled = 1 AND domain_signatures.signature_type = 2 AND user_addresses.address_type=1 UNION
-- default
SELECT "FromOrTo:\tdefault\t %report-dir%/inline.sig.html" rule, 'htmlsigs' collate utf8_unicode_ci as name;

-- select @rownum:=@rownum+1 x, rule from htmlsigs, (SELECT @rownum:=0) r;
-- SELECT @rownum:=@rownum+1 num, rule FROM htmlsigs, (SELECT @rownum:=0) r;
-- SELECT @rownum:=@rownum+1 num, rule FROM ms_rulesets, (SELECT @rownum:=0) r WHERE name='htmlsigs';

-- textsigs.customize
-- Inline Text Signature
CREATE OR REPLACE VIEW textsigs AS
-- email aliases
SELECT CONCAT("From:\t", user_addresses.address, "\t%signature-dir%/users/text/", auth_user.id, ".txt") rule,
'textsigs' collate utf8_unicode_ci as name FROM user_addresses, user_signatures, auth_user WHERE
auth_user.is_active = 1 AND user_addresses.enabled = 1 AND auth_user.id = user_addresses.user_id AND
user_addresses.user_id = auth_user.id AND user_signatures.enabled = 1
AND user_signatures.signature_type = 1 AND user_addresses.address_type = 2 UNION
-- user email
SELECT CONCAT("From:\t", auth_user.email, "\t%signature-dir%/users/text/", auth_user.id, ".txt") rule,
'textsigs' collate utf8_unicode_ci as name FROM user_signatures, auth_user, profiles WHERE 
auth_user.is_active = 1 AND auth_user.id = profiles.user_id AND
user_signatures.user_id = auth_user.id AND user_signatures.enabled = 1
AND user_signatures.signature_type = 1 UNION
-- domains
SELECT CONCAT("From:\t", '*@', user_addresses.address, "\t%signature-dir%/domains/text/", user_addresses.id, ".txt") rule,
'textsigs' collate utf8_unicode_ci as name FROM domain_signatures INNER JOIN user_addresses ON
domain_signatures.useraddress_id = user_addresses.id WHERE domain_signatures.enabled = 1 AND
domain_signatures.signature_type = 1 AND user_addresses.address_type=1 UNION
-- default
SELECT "FromOrTo:\tdefault\t %report-dir%/inline.sig.txt" rule, 'textsigs' collate utf8_unicode_ci as name;

-- sigimgfiles.customize
-- Signature Image Filename
CREATE OR REPLACE VIEW sigimgfiles AS
-- email aliases
SELECT CONCAT("From:\t", user_addresses.address, "\t%signature-dir%/users/imgs/", signature_imgs.name) rule,
'sigimgfiles' collate utf8_unicode_ci as name FROM user_addresses, signature_imgs, profiles, auth_user, 
user_signatures WHERE auth_user.is_active = 1 AND auth_user.id = profiles.user_id AND
profiles.user_id = signature_imgs.owner_id AND signature_imgs.owner_id = user_addresses.user_id
AND user_signatures.user_id = auth_user.id AND profiles.account_type = 3 AND
user_addresses.address_type = 2 AND user_signatures.enabled = 1 AND
user_signatures.signature_type = 2 UNION
-- user email
SELECT CONCAT("From:\t", auth_user.email, "\t%signature-dir%/users/imgs/", signature_imgs.name) rule,
'sigimgfiles' collate utf8_unicode_ci as name FROM signature_imgs, auth_user, profiles, user_signatures WHERE 
auth_user.is_active = 1 AND auth_user.id = profiles.user_id AND profiles.account_type = 3
AND signature_imgs.owner_id = auth_user.id AND user_signatures.user_id = auth_user.id AND
user_signatures.enabled = 1 AND user_signatures.signature_type = 2 UNION
-- domains
SELECT CONCAT("From:\t", '*@', user_addresses.address, "\t%signature-dir%/domains/imgs/", signature_imgs.name) rule,
'sigimgfiles' collate utf8_unicode_ci as name FROM signature_imgs, domain_signatures, user_addresses WHERE
user_addresses.enabled = 1 AND domain_signatures.image_id = signature_imgs.id AND
domain_signatures.useraddress_id = user_addresses.id AND user_addresses.address_type = 1 UNION
-- default
SELECT "FromOrTo:\tdefault\tno" rule, 'sigimgfiles' collate utf8_unicode_ci as name;

-- sigimgs.customize
-- Signature Image <img> Filename
CREATE OR REPLACE VIEW sigimgs AS
-- email aliases
SELECT CONCAT("From:\t", user_addresses.address, "\t", signature_imgs.name) rule,
'sigimgs' collate utf8_unicode_ci as name FROM user_addresses, signature_imgs,
profiles, auth_user, user_signatures WHERE auth_user.is_active = 1 AND
auth_user.id = profiles.user_id AND profiles.user_id = signature_imgs.owner_id AND
signature_imgs.owner_id = user_addresses.user_id AND user_signatures.user_id = auth_user.id AND
profiles.account_type = 3 AND user_addresses.address_type = 2 AND user_signatures.enabled = 1 AND
user_signatures.signature_type = 2 UNION
-- user email
SELECT CONCAT("From:\t", auth_user.email, "\t", signature_imgs.name) rule,
'sigimgs' collate utf8_unicode_ci as name FROM signature_imgs, auth_user, profiles, user_signatures WHERE 
auth_user.is_active = 1 AND auth_user.id = profiles.user_id AND profiles.account_type = 3
AND signature_imgs.owner_id = auth_user.id AND user_signatures.user_id = auth_user.id AND
user_signatures.enabled = 1 AND user_signatures.signature_type = 2 UNION
-- domains
SELECT CONCAT("From:\t", '*@', user_addresses.address, "\t", signature_imgs.name) rule,
'sigimgs' collate utf8_unicode_ci as name FROM signature_imgs, domain_signatures, user_addresses WHERE
user_addresses.enabled = 1 AND domain_signatures.image_id = signature_imgs.id AND
domain_signatures.useraddress_id = user_addresses.id AND user_addresses.address_type = 1 UNION
-- default
SELECT "FromOrTo:\tdefault\tno" rule, 'sigimgs' collate utf8_unicode_ci as name;

-- ms_rulesets
CREATE OR REPLACE VIEW ms_rulesets AS
-- htmlsigs
SELECT * FROM htmlsigs UNION
-- textsigs
SELECT * FROM textsigs UNION
-- sigimgfiles
SELECT * FROM sigimgfiles UNION
-- sigimgs
SELECT * FROM sigimgs;